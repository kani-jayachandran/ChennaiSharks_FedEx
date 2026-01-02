const jwt = require('jsonwebtoken');
const User = require('../models/User');
const logger = require('../utils/logger');

// Middleware to verify JWT token
const authenticate = async (req, res, next) => {
  try {
    let token;
    
    // Get token from header
    if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
      token = req.headers.authorization.split(' ')[1];
    }
    
    // Check if token exists
    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'Access denied. No token provided.'
      });
    }
    
    try {
      // Verify token
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      
      // Get user from database
      const user = await User.findById(decoded.id).select('+password');
      
      if (!user) {
        return res.status(401).json({
          success: false,
          message: 'Token is invalid. User not found.'
        });
      }
      
      // Check if user is active
      if (!user.isActive) {
        return res.status(401).json({
          success: false,
          message: 'Account is deactivated. Please contact administrator.'
        });
      }
      
      // Check if user account is locked
      if (user.isLocked) {
        return res.status(401).json({
          success: false,
          message: 'Account is temporarily locked due to multiple failed login attempts.'
        });
      }
      
      // Check if password was changed after token was issued
      if (user.changedPasswordAfter(decoded.iat)) {
        return res.status(401).json({
          success: false,
          message: 'Password was recently changed. Please log in again.'
        });
      }
      
      // Update last activity
      user.lastActivity = new Date();
      await user.save({ validateBeforeSave: false });
      
      // Add user to request object
      req.user = user;
      next();
      
    } catch (jwtError) {
      if (jwtError.name === 'TokenExpiredError') {
        return res.status(401).json({
          success: false,
          message: 'Token has expired. Please log in again.',
          code: 'TOKEN_EXPIRED'
        });
      } else if (jwtError.name === 'JsonWebTokenError') {
        return res.status(401).json({
          success: false,
          message: 'Invalid token format.',
          code: 'INVALID_TOKEN'
        });
      } else {
        throw jwtError;
      }
    }
    
  } catch (error) {
    logger.logError(error, req);
    return res.status(500).json({
      success: false,
      message: 'Authentication error occurred.'
    });
  }
};

// Middleware to check user roles
const authorize = (...roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: 'Authentication required.'
      });
    }
    
    if (!roles.includes(req.user.role)) {
      logger.logSecurity('Unauthorized access attempt', {
        userId: req.user.id,
        role: req.user.role,
        requiredRoles: roles,
        endpoint: req.originalUrl,
        method: req.method,
        ip: req.ip
      });
      
      return res.status(403).json({
        success: false,
        message: 'Access denied. Insufficient permissions.'
      });
    }
    
    next();
  };
};

// Middleware to check specific permissions
const requirePermission = (permission) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: 'Authentication required.'
      });
    }
    
    if (!req.user.hasPermission(permission)) {
      logger.logSecurity('Permission denied', {
        userId: req.user.id,
        role: req.user.role,
        requiredPermission: permission,
        userPermissions: req.user.permissions,
        endpoint: req.originalUrl,
        method: req.method,
        ip: req.ip
      });
      
      return res.status(403).json({
        success: false,
        message: `Access denied. Required permission: ${permission}`
      });
    }
    
    next();
  };
};

// Middleware to check DCA association for DCA users
const requireDCAAssociation = async (req, res, next) => {
  try {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: 'Authentication required.'
      });
    }
    
    // Only apply to DCA users
    if (req.user.role === 'dca_user') {
      if (!req.user.dcaId) {
        return res.status(403).json({
          success: false,
          message: 'DCA association required.'
        });
      }
      
      // Verify DCA exists and is active
      const DCA = require('../models/DCA');
      const dca = await DCA.findById(req.user.dcaId);
      
      if (!dca || dca.status !== 'ACTIVE') {
        return res.status(403).json({
          success: false,
          message: 'Associated DCA is not active.'
        });
      }
      
      // Add DCA to request object for convenience
      req.dca = dca;
    }
    
    next();
  } catch (error) {
    logger.logError(error, req);
    return res.status(500).json({
      success: false,
      message: 'DCA association check failed.'
    });
  }
};

// Middleware to validate refresh token
const validateRefreshToken = async (req, res, next) => {
  try {
    const { refreshToken } = req.body;
    
    if (!refreshToken) {
      return res.status(401).json({
        success: false,
        message: 'Refresh token is required.'
      });
    }
    
    try {
      // Verify refresh token
      const decoded = jwt.verify(refreshToken, process.env.JWT_SECRET);
      
      if (decoded.type !== 'refresh') {
        return res.status(401).json({
          success: false,
          message: 'Invalid token type.'
        });
      }
      
      // Get user and check if refresh token exists
      const user = await User.findById(decoded.id);
      
      if (!user) {
        return res.status(401).json({
          success: false,
          message: 'User not found.'
        });
      }
      
      // Check if refresh token exists in user's tokens
      const tokenExists = user.refreshTokens.some(
        tokenObj => tokenObj.token === refreshToken && tokenObj.expiresAt > new Date()
      );
      
      if (!tokenExists) {
        return res.status(401).json({
          success: false,
          message: 'Invalid or expired refresh token.'
        });
      }
      
      req.user = user;
      req.refreshToken = refreshToken;
      next();
      
    } catch (jwtError) {
      return res.status(401).json({
        success: false,
        message: 'Invalid refresh token.',
        code: 'INVALID_REFRESH_TOKEN'
      });
    }
    
  } catch (error) {
    logger.logError(error, req);
    return res.status(500).json({
      success: false,
      message: 'Refresh token validation failed.'
    });
  }
};

// Middleware to log user activities
const logActivity = (action) => {
  return (req, res, next) => {
    // Store original res.json to intercept response
    const originalJson = res.json;
    
    res.json = function(data) {
      // Log activity if request was successful
      if (res.statusCode >= 200 && res.statusCode < 300) {
        logger.logActivity(action, req.user?.id, {
          method: req.method,
          url: req.originalUrl,
          ip: req.ip,
          userAgent: req.get('User-Agent'),
          statusCode: res.statusCode
        });
      }
      
      // Call original res.json
      return originalJson.call(this, data);
    };
    
    next();
  };
};

// Middleware for optional authentication (doesn't fail if no token)
const optionalAuth = async (req, res, next) => {
  try {
    let token;
    
    if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
      token = req.headers.authorization.split(' ')[1];
    }
    
    if (token) {
      try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        const user = await User.findById(decoded.id);
        
        if (user && user.isActive && !user.isLocked) {
          req.user = user;
        }
      } catch (jwtError) {
        // Ignore JWT errors for optional auth
      }
    }
    
    next();
  } catch (error) {
    // Continue without authentication for optional auth
    next();
  }
};

module.exports = {
  authenticate,
  authorize,
  requirePermission,
  requireDCAAssociation,
  validateRefreshToken,
  logActivity,
  optionalAuth
};