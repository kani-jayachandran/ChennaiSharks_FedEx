const express = require('express');
const { body, validationResult } = require('express-validator');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');
const User = require('../models/User');
const { authenticate, validateRefreshToken, logActivity } = require('../middleware/auth');
const { catchAsync, AppError, handleValidationError } = require('../middleware/errorHandler');
const logger = require('../utils/logger');

const router = express.Router();

// Validation rules
const registerValidation = [
  body('firstName')
    .trim()
    .isLength({ min: 2, max: 50 })
    .withMessage('First name must be between 2 and 50 characters'),
  body('lastName')
    .trim()
    .isLength({ min: 2, max: 50 })
    .withMessage('Last name must be between 2 and 50 characters'),
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email address'),
  body('password')
    .isLength({ min: 8 })
    .withMessage('Password must be at least 8 characters long')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
    .withMessage('Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character'),
  body('role')
    .isIn(['admin', 'enterprise_manager', 'dca_user'])
    .withMessage('Invalid role specified'),
  body('organization')
    .optional()
    .trim()
    .isLength({ min: 2, max: 100 })
    .withMessage('Organization name must be between 2 and 100 characters'),
  body('dcaId')
    .optional()
    .isMongoId()
    .withMessage('Invalid DCA ID format')
];

const loginValidation = [
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email address'),
  body('password')
    .notEmpty()
    .withMessage('Password is required')
];

const changePasswordValidation = [
  body('currentPassword')
    .notEmpty()
    .withMessage('Current password is required'),
  body('newPassword')
    .isLength({ min: 8 })
    .withMessage('New password must be at least 8 characters long')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
    .withMessage('New password must contain at least one uppercase letter, one lowercase letter, one number, and one special character')
];

// @desc    Register a new user
// @route   POST /api/auth/register
// @access  Public (but may require admin approval)
router.post('/register', registerValidation, catchAsync(async (req, res) => {
  // Check for validation errors
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    throw handleValidationError(errors);
  }

  const {
    firstName,
    lastName,
    email,
    password,
    role,
    organization,
    department,
    position,
    phone,
    dcaId
  } = req.body;

  // Check if user already exists
  const existingUser = await User.findByEmail(email);
  if (existingUser) {
    throw new AppError('User with this email already exists', 400);
  }

  // Validate DCA association for DCA users
  if (role === 'dca_user') {
    if (!dcaId) {
      throw new AppError('DCA ID is required for DCA users', 400);
    }

    const DCA = require('../models/DCA');
    const dca = await DCA.findById(dcaId);
    if (!dca) {
      throw new AppError('Invalid DCA ID', 400);
    }
    if (dca.status !== 'ACTIVE') {
      throw new AppError('Cannot register with inactive DCA', 400);
    }
  }

  // Create user
  const userData = {
    firstName,
    lastName,
    email,
    password,
    role,
    organization,
    department,
    position,
    phone,
    dcaId: role === 'dca_user' ? dcaId : undefined
  };

  const user = await User.create(userData);

  // Generate tokens
  const token = user.generateAuthToken();
  const refreshToken = user.generateRefreshToken(req.get('User-Agent'));
  await user.save();

  // Log registration
  logger.logActivity('USER_REGISTERED', user.id, {
    email: user.email,
    role: user.role,
    ip: req.ip
  });

  // Remove password from response
  user.password = undefined;

  res.status(201).json({
    success: true,
    message: 'User registered successfully',
    data: {
      user,
      token,
      refreshToken
    }
  });
}));

// @desc    Login user
// @route   POST /api/auth/login
// @access  Public
router.post('/login', loginValidation, catchAsync(async (req, res) => {
  // Check for validation errors
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    throw handleValidationError(errors);
  }

  const { email, password } = req.body;

  // Find user and include password
  const user = await User.findByEmail(email).select('+password');
  
  if (!user) {
    // Log failed login attempt
    logger.logSecurity('Failed login attempt - user not found', {
      email,
      ip: req.ip,
      userAgent: req.get('User-Agent')
    });
    
    throw new AppError('Invalid email or password', 401);
  }

  // Check if account is locked
  if (user.isLocked) {
    logger.logSecurity('Login attempt on locked account', {
      userId: user.id,
      email: user.email,
      ip: req.ip
    });
    
    throw new AppError('Account is temporarily locked due to multiple failed login attempts', 423);
  }

  // Check if account is active
  if (!user.isActive) {
    logger.logSecurity('Login attempt on inactive account', {
      userId: user.id,
      email: user.email,
      ip: req.ip
    });
    
    throw new AppError('Account is deactivated. Please contact administrator', 401);
  }

  // Check password
  const isPasswordCorrect = await user.comparePassword(password);
  
  if (!isPasswordCorrect) {
    // Increment login attempts
    await user.incLoginAttempts();
    
    logger.logSecurity('Failed login attempt - incorrect password', {
      userId: user.id,
      email: user.email,
      loginAttempts: user.loginAttempts + 1,
      ip: req.ip
    });
    
    throw new AppError('Invalid email or password', 401);
  }

  // Reset login attempts on successful login
  if (user.loginAttempts > 0) {
    await user.resetLoginAttempts();
  }

  // Generate tokens
  const token = user.generateAuthToken();
  const refreshToken = user.generateRefreshToken(req.get('User-Agent'));
  
  // Update last login
  user.lastLogin = new Date();
  user.lastActivity = new Date();
  await user.save();

  // Log successful login
  logger.logActivity('USER_LOGIN', user.id, {
    email: user.email,
    ip: req.ip,
    userAgent: req.get('User-Agent')
  });

  // Remove password from response
  user.password = undefined;

  res.json({
    success: true,
    message: 'Login successful',
    data: {
      user,
      token,
      refreshToken
    }
  });
}));

// @desc    Refresh access token
// @route   POST /api/auth/refresh
// @access  Public
router.post('/refresh', validateRefreshToken, catchAsync(async (req, res) => {
  const { user, refreshToken } = req;

  // Generate new access token
  const newToken = user.generateAuthToken();

  // Optionally rotate refresh token
  const shouldRotateRefreshToken = Math.random() < 0.1; // 10% chance
  let newRefreshToken = refreshToken;

  if (shouldRotateRefreshToken) {
    // Remove old refresh token
    user.refreshTokens = user.refreshTokens.filter(
      tokenObj => tokenObj.token !== refreshToken
    );
    
    // Generate new refresh token
    newRefreshToken = user.generateRefreshToken(req.get('User-Agent'));
    await user.save();
  }

  // Update last activity
  user.lastActivity = new Date();
  await user.save({ validateBeforeSave: false });

  res.json({
    success: true,
    message: 'Token refreshed successfully',
    data: {
      token: newToken,
      refreshToken: newRefreshToken
    }
  });
}));

// @desc    Logout user
// @route   POST /api/auth/logout
// @access  Private
router.post('/logout', authenticate, logActivity('USER_LOGOUT'), catchAsync(async (req, res) => {
  const { refreshToken } = req.body;

  if (refreshToken) {
    // Remove specific refresh token
    req.user.refreshTokens = req.user.refreshTokens.filter(
      tokenObj => tokenObj.token !== refreshToken
    );
  } else {
    // Remove all refresh tokens (logout from all devices)
    req.user.refreshTokens = [];
  }

  await req.user.save({ validateBeforeSave: false });

  logger.logActivity('USER_LOGOUT', req.user.id, {
    ip: req.ip,
    allDevices: !refreshToken
  });

  res.json({
    success: true,
    message: 'Logout successful'
  });
}));

// @desc    Get current user profile
// @route   GET /api/auth/me
// @access  Private
router.get('/me', authenticate, catchAsync(async (req, res) => {
  // Populate DCA information if user is DCA user
  let user = req.user;
  if (user.role === 'dca_user' && user.dcaId) {
    user = await User.findById(user.id).populate('dcaId', 'name registrationNumber status');
  }

  res.json({
    success: true,
    data: {
      user
    }
  });
}));

// @desc    Update user profile
// @route   PUT /api/auth/profile
// @access  Private
router.put('/profile', authenticate, [
  body('firstName').optional().trim().isLength({ min: 2, max: 50 }),
  body('lastName').optional().trim().isLength({ min: 2, max: 50 }),
  body('phone').optional().trim().matches(/^\+?[\d\s\-\(\)]+$/),
  body('timezone').optional().trim(),
  body('preferences').optional().isObject()
], logActivity('PROFILE_UPDATE'), catchAsync(async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    throw handleValidationError(errors);
  }

  const allowedUpdates = ['firstName', 'lastName', 'phone', 'timezone', 'preferences'];
  const updates = {};

  allowedUpdates.forEach(field => {
    if (req.body[field] !== undefined) {
      updates[field] = req.body[field];
    }
  });

  const user = await User.findByIdAndUpdate(
    req.user.id,
    { ...updates, updatedBy: req.user.id },
    { new: true, runValidators: true }
  );

  res.json({
    success: true,
    message: 'Profile updated successfully',
    data: {
      user
    }
  });
}));

// @desc    Change password
// @route   PUT /api/auth/change-password
// @access  Private
router.put('/change-password', authenticate, changePasswordValidation, logActivity('PASSWORD_CHANGE'), catchAsync(async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    throw handleValidationError(errors);
  }

  const { currentPassword, newPassword } = req.body;

  // Get user with password
  const user = await User.findById(req.user.id).select('+password');

  // Check current password
  const isCurrentPasswordCorrect = await user.comparePassword(currentPassword);
  if (!isCurrentPasswordCorrect) {
    throw new AppError('Current password is incorrect', 400);
  }

  // Check if new password is different
  const isSamePassword = await user.comparePassword(newPassword);
  if (isSamePassword) {
    throw new AppError('New password must be different from current password', 400);
  }

  // Update password
  user.password = newPassword;
  user.passwordChangedAt = new Date();
  
  // Invalidate all refresh tokens
  user.refreshTokens = [];
  
  await user.save();

  logger.logSecurity('Password changed', {
    userId: user.id,
    email: user.email,
    ip: req.ip
  });

  res.json({
    success: true,
    message: 'Password changed successfully. Please log in again with your new password.'
  });
}));

// @desc    Forgot password
// @route   POST /api/auth/forgot-password
// @access  Public
router.post('/forgot-password', [
  body('email').isEmail().normalizeEmail().withMessage('Please provide a valid email address')
], catchAsync(async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    throw handleValidationError(errors);
  }

  const { email } = req.body;

  const user = await User.findByEmail(email);
  if (!user) {
    // Don't reveal if user exists or not
    return res.json({
      success: true,
      message: 'If an account with that email exists, a password reset link has been sent.'
    });
  }

  // Generate reset token
  const resetToken = crypto.randomBytes(32).toString('hex');
  user.passwordResetToken = crypto.createHash('sha256').update(resetToken).digest('hex');
  user.passwordResetExpires = new Date(Date.now() + 10 * 60 * 1000); // 10 minutes

  await user.save({ validateBeforeSave: false });

  logger.logSecurity('Password reset requested', {
    userId: user.id,
    email: user.email,
    ip: req.ip
  });

  // In a real application, send email with reset link
  // For now, just return success (in development, you might return the token)
  const responseData = {
    success: true,
    message: 'If an account with that email exists, a password reset link has been sent.'
  };

  // Include reset token in development mode
  if (process.env.NODE_ENV === 'development') {
    responseData.resetToken = resetToken;
  }

  res.json(responseData);
}));

// @desc    Reset password
// @route   POST /api/auth/reset-password/:token
// @access  Public
router.post('/reset-password/:token', [
  body('password')
    .isLength({ min: 8 })
    .withMessage('Password must be at least 8 characters long')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
    .withMessage('Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character')
], catchAsync(async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    throw handleValidationError(errors);
  }

  const { token } = req.params;
  const { password } = req.body;

  // Hash the token to compare with stored hash
  const hashedToken = crypto.createHash('sha256').update(token).digest('hex');

  // Find user with valid reset token
  const user = await User.findOne({
    passwordResetToken: hashedToken,
    passwordResetExpires: { $gt: Date.now() }
  });

  if (!user) {
    throw new AppError('Invalid or expired reset token', 400);
  }

  // Update password and clear reset token
  user.password = password;
  user.passwordChangedAt = new Date();
  user.passwordResetToken = undefined;
  user.passwordResetExpires = undefined;
  
  // Invalidate all refresh tokens
  user.refreshTokens = [];

  await user.save();

  logger.logSecurity('Password reset completed', {
    userId: user.id,
    email: user.email,
    ip: req.ip
  });

  res.json({
    success: true,
    message: 'Password reset successful. Please log in with your new password.'
  });
}));

module.exports = router;