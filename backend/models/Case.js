const mongoose = require('mongoose');

const caseSchema = new mongoose.Schema({
  // Case Identification
  caseNumber: {
    type: String,
    required: [true, 'Case number is required'],
    unique: true,
    trim: true,
    uppercase: true
  },
  externalCaseId: {
    type: String,
    trim: true,
    index: true
  },
  
  // Customer Information
  customer: {
    customerId: {
      type: String,
      required: [true, 'Customer ID is required'],
      trim: true,
      index: true
    },
    name: {
      type: String,
      required: [true, 'Customer name is required'],
      trim: true
    },
    email: {
      type: String,
      trim: true,
      lowercase: true,
      match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Invalid email format']
    },
    phone: {
      type: String,
      trim: true
    },
    address: {
      street: String,
      city: String,
      state: String,
      zipCode: String,
      country: {
        type: String,
        default: 'US'
      }
    },
    riskProfile: {
      type: String,
      enum: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
      default: 'MEDIUM'
    },
    segment: {
      type: String,
      enum: ['STANDARD', 'VIP', 'CORPORATE', 'SME'],
      default: 'STANDARD'
    }
  },
  
  // Debt Information
  debt: {
    originalAmount: {
      type: Number,
      required: [true, 'Original debt amount is required'],
      min: [0, 'Debt amount cannot be negative']
    },
    currentAmount: {
      type: Number,
      required: [true, 'Current debt amount is required'],
      min: [0, 'Debt amount cannot be negative']
    },
    currency: {
      type: String,
      default: 'USD',
      uppercase: true
    },
    invoiceNumber: {
      type: String,
      trim: true
    },
    invoiceDate: {
      type: Date,
      required: [true, 'Invoice date is required']
    },
    dueDate: {
      type: Date,
      required: [true, 'Due date is required']
    },
    serviceType: {
      type: String,
      enum: ['STANDARD', 'PREMIUM', 'ENTERPRISE', 'SMALL_BUSINESS'],
      default: 'STANDARD'
    },
    description: {
      type: String,
      trim: true
    }
  },
  
  // Case Status and Workflow
  status: {
    type: String,
    enum: [
      'NEW', 'ASSIGNED', 'IN_PROGRESS', 'CONTACTED', 'NEGOTIATING',
      'PAYMENT_PLAN', 'RESOLVED', 'CLOSED', 'ESCALATED', 'LEGAL'
    ],
    default: 'NEW',
    required: true
  },
  priority: {
    type: String,
    enum: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
    default: 'MEDIUM'
  },
  priorityScore: {
    type: Number,
    min: 0,
    max: 100,
    default: 50
  },
  
  // Assignment Information
  assignedDCA: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'DCA',
    index: true
  },
  assignedAgent: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  assignedDate: Date,
  assignmentReason: String,
  
  // SLA and Timing
  sla: {
    responseTime: {
      type: Number, // Hours
      default: 24
    },
    resolutionTime: {
      type: Number, // Hours
      default: 72
    },
    escalationTime: {
      type: Number, // Hours
      default: 48
    }
  },
  
  // Important Dates
  dates: {
    firstContact: Date,
    lastContact: Date,
    expectedResolution: Date,
    actualResolution: Date,
    escalationDate: Date
  },
  
  // Aging Information
  aging: {
    days: {
      type: Number,
      default: 0,
      min: 0
    },
    category: {
      type: String,
      enum: ['FRESH', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
      default: 'FRESH'
    }
  },
  
  // AI/ML Predictions
  predictions: {
    recoveryProbability: {
      type: Number,
      min: 0,
      max: 1,
      default: 0.5
    },
    riskScore: {
      type: Number,
      min: 0,
      max: 100,
      default: 50
    },
    recommendedActions: [String],
    confidence: {
      type: Number,
      min: 0,
      max: 1,
      default: 0.5
    },
    lastPredictionUpdate: Date
  },
  
  // Communication History
  communications: [{
    type: {
      type: String,
      enum: ['EMAIL', 'PHONE', 'SMS', 'LETTER', 'MEETING', 'SYSTEM'],
      required: true
    },
    direction: {
      type: String,
      enum: ['INBOUND', 'OUTBOUND'],
      required: true
    },
    subject: String,
    content: String,
    outcome: {
      type: String,
      enum: ['SUCCESSFUL', 'NO_RESPONSE', 'REFUSED', 'PROMISED_PAYMENT', 'DISPUTE']
    },
    nextAction: String,
    scheduledFollowUp: Date,
    createdBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true
    },
    createdAt: {
      type: Date,
      default: Date.now
    },
    attachments: [{
      filename: String,
      originalName: String,
      mimeType: String,
      size: Number,
      path: String
    }]
  }],
  
  // Payment History
  payments: [{
    amount: {
      type: Number,
      required: true,
      min: 0
    },
    paymentDate: {
      type: Date,
      required: true
    },
    paymentMethod: {
      type: String,
      enum: ['CASH', 'CHECK', 'CREDIT_CARD', 'BANK_TRANSFER', 'ONLINE', 'OTHER']
    },
    transactionId: String,
    status: {
      type: String,
      enum: ['PENDING', 'COMPLETED', 'FAILED', 'REFUNDED'],
      default: 'PENDING'
    },
    notes: String,
    recordedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    recordedAt: {
      type: Date,
      default: Date.now
    }
  }],
  
  // Escalation Information
  escalations: [{
    level: {
      type: Number,
      required: true,
      min: 1
    },
    reason: {
      type: String,
      required: true
    },
    escalatedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true
    },
    escalatedTo: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    escalatedAt: {
      type: Date,
      default: Date.now
    },
    resolvedAt: Date,
    resolution: String,
    status: {
      type: String,
      enum: ['OPEN', 'IN_PROGRESS', 'RESOLVED'],
      default: 'OPEN'
    }
  }],
  
  // Documents and Attachments
  documents: [{
    type: {
      type: String,
      enum: ['INVOICE', 'CONTRACT', 'CORRESPONDENCE', 'PAYMENT_PROOF', 'LEGAL', 'OTHER'],
      required: true
    },
    filename: String,
    originalName: String,
    mimeType: String,
    size: Number,
    path: String,
    uploadedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    uploadedAt: {
      type: Date,
      default: Date.now
    },
    description: String
  }],
  
  // Notes and Comments
  notes: [{
    content: {
      type: String,
      required: true
    },
    type: {
      type: String,
      enum: ['GENERAL', 'IMPORTANT', 'INTERNAL', 'CUSTOMER_FEEDBACK'],
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
  
  // Compliance and Legal
  compliance: {
    regulatoryFlags: [String],
    legalHold: {
      type: Boolean,
      default: false
    },
    disputeStatus: {
      type: String,
      enum: ['NONE', 'PENDING', 'RESOLVED', 'ESCALATED']
    },
    lastComplianceCheck: Date
  },
  
  // Metadata
  metadata: {
    source: {
      type: String,
      enum: ['MANUAL', 'API', 'IMPORT', 'SYSTEM'],
      default: 'MANUAL'
    },
    tags: [String],
    customFields: mongoose.Schema.Types.Mixed
  },
  
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

// Indexes for performance
caseSchema.index({ caseNumber: 1 });
caseSchema.index({ 'customer.customerId': 1 });
caseSchema.index({ status: 1 });
caseSchema.index({ priority: 1 });
caseSchema.index({ assignedDCA: 1 });
caseSchema.index({ assignedAgent: 1 });
caseSchema.index({ 'debt.dueDate': 1 });
caseSchema.index({ 'aging.days': 1 });
caseSchema.index({ createdAt: -1 });
caseSchema.index({ updatedAt: -1 });

// Compound indexes
caseSchema.index({ status: 1, priority: -1 });
caseSchema.index({ assignedDCA: 1, status: 1 });
caseSchema.index({ 'aging.category': 1, status: 1 });

// Virtual for total payments
caseSchema.virtual('totalPaid').get(function() {
  return this.payments
    .filter(payment => payment.status === 'COMPLETED')
    .reduce((total, payment) => total + payment.amount, 0);
});

// Virtual for remaining balance
caseSchema.virtual('remainingBalance').get(function() {
  return Math.max(0, this.debt.currentAmount - this.totalPaid);
});

// Virtual for recovery rate
caseSchema.virtual('recoveryRate').get(function() {
  if (this.debt.originalAmount === 0) return 0;
  return (this.totalPaid / this.debt.originalAmount) * 100;
});

// Virtual for case age in days
caseSchema.virtual('ageInDays').get(function() {
  const now = new Date();
  const created = this.createdAt || now;
  return Math.floor((now - created) / (1000 * 60 * 60 * 24));
});

// Virtual for overdue days
caseSchema.virtual('overdueDays').get(function() {
  const now = new Date();
  const dueDate = this.debt.dueDate;
  if (!dueDate || dueDate > now) return 0;
  return Math.floor((now - dueDate) / (1000 * 60 * 60 * 24));
});

// Pre-save middleware to generate case number
caseSchema.pre('save', async function(next) {
  if (this.isNew && !this.caseNumber) {
    const year = new Date().getFullYear();
    const count = await this.constructor.countDocuments({
      createdAt: {
        $gte: new Date(year, 0, 1),
        $lt: new Date(year + 1, 0, 1)
      }
    });
    this.caseNumber = `CASE-${year}-${String(count + 1).padStart(6, '0')}`;
  }
  next();
});

// Pre-save middleware to update aging information
caseSchema.pre('save', function(next) {
  if (this.debt.dueDate) {
    this.aging.days = this.overdueDays;
    
    // Update aging category
    if (this.aging.days <= 0) {
      this.aging.category = 'FRESH';
    } else if (this.aging.days <= 30) {
      this.aging.category = 'LOW';
    } else if (this.aging.days <= 60) {
      this.aging.category = 'MEDIUM';
    } else if (this.aging.days <= 90) {
      this.aging.category = 'HIGH';
    } else {
      this.aging.category = 'CRITICAL';
    }
  }
  next();
});

// Pre-save middleware to update current debt amount
caseSchema.pre('save', function(next) {
  if (this.payments && this.payments.length > 0) {
    const totalPaid = this.totalPaid;
    this.debt.currentAmount = Math.max(0, this.debt.originalAmount - totalPaid);
  }
  next();
});

// Static method to find cases by status
caseSchema.statics.findByStatus = function(status) {
  return this.find({ status });
};

// Static method to find overdue cases
caseSchema.statics.findOverdue = function() {
  return this.find({
    'debt.dueDate': { $lt: new Date() },
    status: { $nin: ['RESOLVED', 'CLOSED'] }
  });
};

// Static method to find cases by DCA
caseSchema.statics.findByDCA = function(dcaId) {
  return this.find({ assignedDCA: dcaId });
};

// Instance method to add communication
caseSchema.methods.addCommunication = function(communication) {
  this.communications.push(communication);
  this.dates.lastContact = new Date();
  if (!this.dates.firstContact) {
    this.dates.firstContact = new Date();
  }
  return this.save();
};

// Instance method to add payment
caseSchema.methods.addPayment = function(payment) {
  this.payments.push(payment);
  return this.save();
};

// Instance method to escalate case
caseSchema.methods.escalate = function(escalation) {
  this.escalations.push(escalation);
  this.status = 'ESCALATED';
  this.dates.escalationDate = new Date();
  return this.save();
};

// Instance method to update predictions
caseSchema.methods.updatePredictions = function(predictions) {
  this.predictions = { ...this.predictions, ...predictions };
  this.predictions.lastPredictionUpdate = new Date();
  return this.save();
};

module.exports = mongoose.model('Case', caseSchema);