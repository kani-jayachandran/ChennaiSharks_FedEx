const mongoose = require('mongoose');

const dcaSchema = new mongoose.Schema({
  // Basic Information
  name: {
    type: String,
    required: [true, 'DCA name is required'],
    trim: true,
    maxlength: [100, 'DCA name cannot exceed 100 characters']
  },
  legalName: {
    type: String,
    required: [true, 'Legal name is required'],
    trim: true
  },
  registrationNumber: {
    type: String,
    required: [true, 'Registration number is required'],
    unique: true,
    trim: true,
    uppercase: true
  },
  
  // Contact Information
  contact: {
    primaryEmail: {
      type: String,
      required: [true, 'Primary email is required'],
      lowercase: true,
      trim: true,
      match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Invalid email format']
    },
    secondaryEmail: {
      type: String,
      lowercase: true,
      trim: true,
      match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Invalid email format']
    },
    phone: {
      type: String,
      required: [true, 'Phone number is required'],
      trim: true
    },
    fax: {
      type: String,
      trim: true
    },
    website: {
      type: String,
      trim: true,
      match: [/^https?:\/\/.+/, 'Invalid website URL']
    }
  },
  
  // Address Information
  address: {
    street: {
      type: String,
      required: [true, 'Street address is required'],
      trim: true
    },
    city: {
      type: String,
      required: [true, 'City is required'],
      trim: true
    },
    state: {
      type: String,
      required: [true, 'State is required'],
      trim: true
    },
    zipCode: {
      type: String,
      required: [true, 'ZIP code is required'],
      trim: true
    },
    country: {
      type: String,
      required: [true, 'Country is required'],
      default: 'US',
      uppercase: true
    }
  },
  
  // Business Information
  business: {
    type: {
      type: String,
      enum: ['CORPORATION', 'LLC', 'PARTNERSHIP', 'SOLE_PROPRIETORSHIP'],
      required: [true, 'Business type is required']
    },
    taxId: {
      type: String,
      required: [true, 'Tax ID is required'],
      trim: true
    },
    establishedDate: {
      type: Date,
      required: [true, 'Established date is required']
    },
    employeeCount: {
      type: Number,
      min: [1, 'Employee count must be at least 1']
    },
    annualRevenue: {
      type: Number,
      min: [0, 'Annual revenue cannot be negative']
    }
  },
  
  // Licensing and Compliance
  licensing: {
    licenses: [{
      type: {
        type: String,
        enum: ['FEDERAL', 'STATE', 'LOCAL', 'INDUSTRY_SPECIFIC'],
        required: true
      },
      number: {
        type: String,
        required: true,
        trim: true
      },
      issuingAuthority: {
        type: String,
        required: true,
        trim: true
      },
      issueDate: {
        type: Date,
        required: true
      },
      expiryDate: {
        type: Date,
        required: true
      },
      status: {
        type: String,
        enum: ['ACTIVE', 'EXPIRED', 'SUSPENDED', 'REVOKED'],
        default: 'ACTIVE'
      }
    }],
    certifications: [{
      name: {
        type: String,
        required: true,
        trim: true
      },
      issuingBody: {
        type: String,
        required: true,
        trim: true
      },
      certificationDate: {
        type: Date,
        required: true
      },
      expiryDate: Date,
      certificateNumber: String
    }],
    complianceStatus: {
      type: String,
      enum: ['COMPLIANT', 'NON_COMPLIANT', 'UNDER_REVIEW', 'SUSPENDED'],
      default: 'UNDER_REVIEW'
    },
    lastComplianceCheck: Date
  },
  
  // Specializations and Capabilities
  specializations: [{
    type: String,
    enum: [
      'COMMERCIAL_DEBT', 'CONSUMER_DEBT', 'MEDICAL_DEBT', 'STUDENT_LOANS',
      'CREDIT_CARDS', 'AUTOMOTIVE', 'TELECOMMUNICATIONS', 'UTILITIES',
      'RETAIL', 'HEALTHCARE', 'FINANCIAL_SERVICES', 'GOVERNMENT',
      'SMALL_BUSINESS', 'ENTERPRISE', 'INTERNATIONAL'
    ]
  }],
  
  services: [{
    type: String,
    enum: [
      'FIRST_PARTY_COLLECTION', 'THIRD_PARTY_COLLECTION', 'SKIP_TRACING',
      'LEGAL_SERVICES', 'CREDIT_REPORTING', 'PAYMENT_PROCESSING',
      'CUSTOMER_SERVICE', 'DISPUTE_RESOLUTION', 'BANKRUPTCY_SERVICES',
      'ASSET_RECOVERY', 'INTERNATIONAL_COLLECTION'
    ]
  }],
  
  // Capacity and Resources
  capacity: {
    maxConcurrentCases: {
      type: Number,
      required: [true, 'Maximum concurrent cases is required'],
      min: [1, 'Must handle at least 1 case']
    },
    currentCaseLoad: {
      type: Number,
      default: 0,
      min: [0, 'Current case load cannot be negative']
    },
    availableAgents: {
      type: Number,
      required: [true, 'Available agents count is required'],
      min: [1, 'Must have at least 1 agent']
    },
    workingHours: {
      timezone: {
        type: String,
        default: 'UTC'
      },
      schedule: [{
        day: {
          type: String,
          enum: ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'],
          required: true
        },
        startTime: {
          type: String,
          required: true,
          match: [/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/, 'Invalid time format (HH:MM)']
        },
        endTime: {
          type: String,
          required: true,
          match: [/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/, 'Invalid time format (HH:MM)']
        },
        isWorkingDay: {
          type: Boolean,
          default: true
        }
      }]
    }
  },
  
  // Performance Metrics
  performance: {
    // Recovery Metrics
    totalCasesHandled: {
      type: Number,
      default: 0,
      min: 0
    },
    totalAmountRecovered: {
      type: Number,
      default: 0,
      min: 0
    },
    averageRecoveryRate: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    averageRecoveryTime: {
      type: Number, // in days
      default: 0,
      min: 0
    },
    
    // SLA Metrics
    slaCompliance: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    averageResponseTime: {
      type: Number, // in hours
      default: 0,
      min: 0
    },
    averageResolutionTime: {
      type: Number, // in hours
      default: 0,
      min: 0
    },
    
    // Quality Metrics
    customerSatisfactionScore: {
      type: Number,
      default: 0,
      min: 0,
      max: 5
    },
    complaintRate: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    escalationRate: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    
    // Efficiency Metrics
    costPerCase: {
      type: Number,
      default: 0,
      min: 0
    },
    profitMargin: {
      type: Number,
      default: 0
    },
    
    // Historical Performance
    monthlyMetrics: [{
      month: {
        type: Date,
        required: true
      },
      casesHandled: Number,
      amountRecovered: Number,
      recoveryRate: Number,
      slaCompliance: Number,
      customerSatisfaction: Number
    }],
    
    lastUpdated: {
      type: Date,
      default: Date.now
    }
  },
  
  // Scoring and Ranking
  scoring: {
    overallScore: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    performanceScore: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    reliabilityScore: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    efficiencyScore: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    ranking: {
      type: Number,
      default: 0
    },
    lastScoreUpdate: {
      type: Date,
      default: Date.now
    }
  },
  
  // Contract and Financial Terms
  contract: {
    startDate: {
      type: Date,
      required: [true, 'Contract start date is required']
    },
    endDate: Date,
    renewalDate: Date,
    status: {
      type: String,
      enum: ['ACTIVE', 'INACTIVE', 'SUSPENDED', 'TERMINATED', 'PENDING'],
      default: 'PENDING'
    },
    commissionStructure: [{
      tier: {
        type: String,
        required: true
      },
      minAmount: {
        type: Number,
        required: true,
        min: 0
      },
      maxAmount: Number,
      commissionRate: {
        type: Number,
        required: true,
        min: 0,
        max: 100
      }
    }],
    paymentTerms: {
      type: String,
      enum: ['NET_15', 'NET_30', 'NET_45', 'NET_60', 'IMMEDIATE'],
      default: 'NET_30'
    },
    minimumVolume: {
      type: Number,
      default: 0
    }
  },
  
  // Integration and Technical
  integration: {
    apiEnabled: {
      type: Boolean,
      default: false
    },
    apiKey: {
      type: String,
      select: false // Don't include in queries by default
    },
    webhookUrl: {
      type: String,
      trim: true,
      match: [/^https?:\/\/.+/, 'Invalid webhook URL']
    },
    supportedFormats: [{
      type: String,
      enum: ['JSON', 'XML', 'CSV', 'EDI', 'CUSTOM']
    }],
    lastSyncDate: Date,
    syncStatus: {
      type: String,
      enum: ['SUCCESS', 'FAILED', 'IN_PROGRESS', 'NOT_CONFIGURED'],
      default: 'NOT_CONFIGURED'
    }
  },
  
  // Status and Flags
  status: {
    type: String,
    enum: ['ACTIVE', 'INACTIVE', 'SUSPENDED', 'TERMINATED', 'ONBOARDING'],
    default: 'ONBOARDING'
  },
  
  flags: {
    isPreferred: {
      type: Boolean,
      default: false
    },
    isBlacklisted: {
      type: Boolean,
      default: false
    },
    requiresApproval: {
      type: Boolean,
      default: true
    },
    hasActiveIssues: {
      type: Boolean,
      default: false
    }
  },
  
  // Notes and Comments
  notes: [{
    content: {
      type: String,
      required: true
    },
    type: {
      type: String,
      enum: ['GENERAL', 'PERFORMANCE', 'COMPLIANCE', 'CONTRACT', 'TECHNICAL'],
      default: 'GENERAL'
    },
    isPrivate: {
      type: Boolean,
      default: false
    },
    createdBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true
    },
    createdAt: {
      type: Date,
      default: Date.now
    }
  }],
  
  // Audit Fields
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  updatedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Indexes
dcaSchema.index({ registrationNumber: 1 });
dcaSchema.index({ name: 1 });
dcaSchema.index({ status: 1 });
dcaSchema.index({ 'contract.status': 1 });
dcaSchema.index({ 'scoring.overallScore': -1 });
dcaSchema.index({ 'performance.averageRecoveryRate': -1 });
dcaSchema.index({ specializations: 1 });
dcaSchema.index({ createdAt: -1 });

// Virtual for capacity utilization
dcaSchema.virtual('capacityUtilization').get(function() {
  if (this.capacity.maxConcurrentCases === 0) return 0;
  return (this.capacity.currentCaseLoad / this.capacity.maxConcurrentCases) * 100;
});

// Virtual for available capacity
dcaSchema.virtual('availableCapacity').get(function() {
  return Math.max(0, this.capacity.maxConcurrentCases - this.capacity.currentCaseLoad);
});

// Virtual for years in business
dcaSchema.virtual('yearsInBusiness').get(function() {
  if (!this.business.establishedDate) return 0;
  const now = new Date();
  const established = this.business.establishedDate;
  return Math.floor((now - established) / (1000 * 60 * 60 * 24 * 365.25));
});

// Virtual for license status
dcaSchema.virtual('hasValidLicenses').get(function() {
  if (!this.licensing.licenses || this.licensing.licenses.length === 0) return false;
  
  const now = new Date();
  return this.licensing.licenses.every(license => 
    license.status === 'ACTIVE' && 
    (!license.expiryDate || license.expiryDate > now)
  );
});

// Pre-save middleware to update capacity utilization
dcaSchema.pre('save', function(next) {
  // Ensure current case load doesn't exceed max capacity
  if (this.capacity.currentCaseLoad > this.capacity.maxConcurrentCases) {
    this.capacity.currentCaseLoad = this.capacity.maxConcurrentCases;
  }
  next();
});

// Pre-save middleware to update compliance status
dcaSchema.pre('save', function(next) {
  if (this.isModified('licensing.licenses')) {
    this.licensing.complianceStatus = this.hasValidLicenses ? 'COMPLIANT' : 'NON_COMPLIANT';
  }
  next();
});

// Static method to find active DCAs
dcaSchema.statics.findActive = function() {
  return this.find({ 
    status: 'ACTIVE',
    'contract.status': 'ACTIVE',
    'flags.isBlacklisted': false
  });
};

// Static method to find DCAs by specialization
dcaSchema.statics.findBySpecialization = function(specialization) {
  return this.find({ 
    specializations: specialization,
    status: 'ACTIVE'
  });
};

// Static method to find available DCAs
dcaSchema.statics.findAvailable = function(minCapacity = 1) {
  return this.find({
    status: 'ACTIVE',
    'contract.status': 'ACTIVE',
    'flags.isBlacklisted': false,
    $expr: {
      $gte: [
        { $subtract: ['$capacity.maxConcurrentCases', '$capacity.currentCaseLoad'] },
        minCapacity
      ]
    }
  });
};

// Instance method to update performance metrics
dcaSchema.methods.updatePerformanceMetrics = function(metrics) {
  Object.assign(this.performance, metrics);
  this.performance.lastUpdated = new Date();
  return this.save();
};

// Instance method to update scoring
dcaSchema.methods.updateScoring = function(scores) {
  Object.assign(this.scoring, scores);
  this.scoring.lastScoreUpdate = new Date();
  return this.save();
};

// Instance method to add monthly metrics
dcaSchema.methods.addMonthlyMetrics = function(monthlyData) {
  this.performance.monthlyMetrics.push(monthlyData);
  
  // Keep only last 24 months
  if (this.performance.monthlyMetrics.length > 24) {
    this.performance.monthlyMetrics = this.performance.monthlyMetrics.slice(-24);
  }
  
  return this.save();
};

// Instance method to check availability
dcaSchema.methods.isAvailable = function(requiredCapacity = 1) {
  return this.status === 'ACTIVE' &&
         this.contract.status === 'ACTIVE' &&
         !this.flags.isBlacklisted &&
         this.availableCapacity >= requiredCapacity;
};

// Instance method to assign case
dcaSchema.methods.assignCase = function() {
  if (this.availableCapacity > 0) {
    this.capacity.currentCaseLoad += 1;
    return this.save();
  }
  throw new Error('No available capacity');
};

// Instance method to release case
dcaSchema.methods.releaseCase = function() {
  if (this.capacity.currentCaseLoad > 0) {
    this.capacity.currentCaseLoad -= 1;
    return this.save();
  }
  return this.save();
};

module.exports = mongoose.model('DCA', dcaSchema);