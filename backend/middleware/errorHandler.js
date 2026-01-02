const logger = require('../utils/logger');

// Custom error class
class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';
    this.isOperational = true;

    Error.captureStackTrace(this, this.constructor);
  }
}

// Handle Mongoose CastError (Invalid ObjectId)
const handleCastErrorDB = (err) => {
  const message = `Invalid ${err.path}: ${err.value}`;
  return new AppError(message, 400);
};

// Handle Mongoose Duplicate Key Error
const handleDuplicateFieldsDB = (err) => {
  const field = Object.keys(err.keyValue)[0];
  const value = err.keyValue[field];
  const message = `Duplicate field value: ${field} = '${value}'. Please use another value.`;
  return new AppError(message, 400);
};

// Handle Mongoose Validation Error
const handleValidationErrorDB = (err) => {
  const errors = Object.values(err.errors).map(el => el.message);
  const message = `Invalid input data. ${errors.join('. ')}`;
  return new AppError(message, 400);
};

// Handle JWT Error
const handleJWTError = () =>
  new AppError('Invalid token. Please log in again.', 401);

// Handle JWT Expired Error
const handleJWTExpiredError = () =>
  new AppError('Your token has expired. Please log in again.', 401);

// Send error response for development
const sendErrorDev = (err, req, res) => {
  // Log error details
  logger.logError(err, req);

  // API Error
  if (req.originalUrl.startsWith('/api')) {
    return res.status(err.statusCode).json({
      success: false,
      error: err,
      message: err.message,
      stack: err.stack,
      timestamp: new Date().toISOString(),
      path: req.originalUrl,
      method: req.method
    });
  }

  // Rendered website error (if serving HTML)
  return res.status(err.statusCode).json({
    success: false,
    message: 'Something went wrong!',
    error: err.message
  });
};

// Send error response for production
const sendErrorProd = (err, req, res) => {
  // API Error
  if (req.originalUrl.startsWith('/api')) {
    // Operational, trusted error: send message to client
    if (err.isOperational) {
      return res.status(err.statusCode).json({
        success: false,
        message: err.message,
        timestamp: new Date().toISOString()
      });
    }

    // Programming or other unknown error: don't leak error details
    logger.logError(err, req);
    
    return res.status(500).json({
      success: false,
      message: 'Something went wrong!',
      timestamp: new Date().toISOString()
    });
  }

  // Rendered website error
  if (err.isOperational) {
    return res.status(err.statusCode).json({
      success: false,
      message: err.message
    });
  }

  // Programming or other unknown error
  logger.logError(err, req);
  
  return res.status(500).json({
    success: false,
    message: 'Something went wrong!'
  });
};

// Global error handling middleware
const globalErrorHandler = (err, req, res, next) => {
  err.statusCode = err.statusCode || 500;
  err.status = err.status || 'error';

  if (process.env.NODE_ENV === 'development') {
    sendErrorDev(err, req, res);
  } else {
    let error = { ...err };
    error.message = err.message;

    // Handle specific error types
    if (error.name === 'CastError') error = handleCastErrorDB(error);
    if (error.code === 11000) error = handleDuplicateFieldsDB(error);
    if (error.name === 'ValidationError') error = handleValidationErrorDB(error);
    if (error.name === 'JsonWebTokenError') error = handleJWTError();
    if (error.name === 'TokenExpiredError') error = handleJWTExpiredError();

    sendErrorProd(error, req, res);
  }
};

// Async error handler wrapper
const catchAsync = (fn) => {
  return (req, res, next) => {
    fn(req, res, next).catch(next);
  };
};

// 404 handler for undefined routes
const notFound = (req, res, next) => {
  const err = new AppError(`Can't find ${req.originalUrl} on this server!`, 404);
  next(err);
};

// Validation error handler
const handleValidationError = (errors) => {
  const formattedErrors = errors.array().map(error => ({
    field: error.param,
    message: error.msg,
    value: error.value
  }));

  return new AppError(`Validation failed: ${formattedErrors.map(e => e.message).join(', ')}`, 400);
};

// Rate limit error handler
const handleRateLimitError = (req, res) => {
  logger.logSecurity('Rate limit exceeded', {
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    endpoint: req.originalUrl,
    method: req.method
  });

  return res.status(429).json({
    success: false,
    message: 'Too many requests from this IP, please try again later.',
    retryAfter: Math.ceil((parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000) / 1000)
  });
};

// Database connection error handler
const handleDBConnectionError = (error) => {
  logger.error('Database connection error:', error);
  
  return new AppError('Database connection failed. Please try again later.', 503);
};

// File upload error handler
const handleFileUploadError = (error) => {
  if (error.code === 'LIMIT_FILE_SIZE') {
    return new AppError('File too large. Maximum size allowed is 10MB.', 400);
  }
  
  if (error.code === 'LIMIT_FILE_COUNT') {
    return new AppError('Too many files. Maximum 10 files allowed.', 400);
  }
  
  if (error.code === 'LIMIT_UNEXPECTED_FILE') {
    return new AppError('Unexpected file field.', 400);
  }
  
  return new AppError('File upload failed.', 400);
};

// External API error handler
const handleExternalAPIError = (error, service) => {
  logger.error(`External API error (${service}):`, error);
  
  if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
    return new AppError(`${service} service is currently unavailable.`, 503);
  }
  
  if (error.response && error.response.status >= 400) {
    return new AppError(`${service} service error: ${error.response.statusText}`, 502);
  }
  
  return new AppError(`${service} service error occurred.`, 502);
};

module.exports = {
  AppError,
  globalErrorHandler,
  catchAsync,
  notFound,
  handleValidationError,
  handleRateLimitError,
  handleDBConnectionError,
  handleFileUploadError,
  handleExternalAPIError
};