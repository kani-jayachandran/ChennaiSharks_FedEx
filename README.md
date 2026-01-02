# Enterprise DCA Management Platform

## Overview
A comprehensive web-based Debt Collection Agency (DCA) Management Platform designed for large logistics enterprises like FedEx. This system centralizes end-to-end case management, replacing manual spreadsheets and email-based processes with intelligent automation, AI-driven insights, and enterprise-grade security.

## Key Features

### 🎯 Core Capabilities
- **Centralized Case Management**: End-to-end lifecycle from ingestion to closure
- **Intelligent Allocation**: AI-powered case assignment to optimal DCAs
- **SOP-Driven Workflows**: Automated state transitions with SLA enforcement
- **Role-Based Access Control**: Secure portals for Admin, Enterprise Managers, and DCAs
- **Real-Time Analytics**: Interactive dashboards with predictive insights
- **Audit Trail**: Complete traceability of all actions and decisions

### 🤖 AI/ML Components
- **Recovery Probability Predictor**: Estimates likelihood of successful recovery
- **Case Prioritization Engine**: Ranks cases by business impact and recovery potential
- **DCA Performance Scorer**: Continuous evaluation of agency effectiveness
- **Predictive Analytics**: Trend analysis and risk assessment

### 📊 Analytics & Reporting
- Total overdue value tracking
- Aging bucket analysis
- Recovery trend monitoring
- DCA performance metrics
- SLA compliance dashboards
- Escalation risk indicators

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │    AI/ML        │
│   (React)       │◄──►│   (Node.js)     │◄──►│   (Python)      │
│                 │    │                 │    │                 │
│ • Dashboards    │    │ • REST APIs     │    │ • Recovery      │
│ • Case Mgmt     │    │ • Auth/RBAC     │    │   Predictor     │
│ • Analytics     │    │ • Workflow      │    │ • Prioritizer   │
│ • Notifications │    │ • SLA Engine    │    │ • DCA Scorer    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │    Database     │
                    │   (MongoDB)     │
                    │                 │
                    │ • Cases         │
                    │ • Users         │
                    │ • DCAs          │
                    │ • Analytics     │
                    └─────────────────┘
```

## Technology Stack

### Frontend
- **React 18** with TypeScript
- **Material-UI (MUI)** for enterprise UI components
- **Recharts** for analytics visualization
- **React Router** for navigation
- **Axios** for API communication

### Backend
- **Node.js** with Express.js
- **MongoDB** with Mongoose ODM
- **JWT** for authentication
- **Winston** for logging
- **Node-cron** for scheduled tasks

### AI/ML Services
- **Python** with FastAPI
- **scikit-learn** for ML models
- **pandas/numpy** for data processing
- **joblib** for model persistence

### DevOps & Security
- **Docker** containerization
- **CORS** configuration
- **Rate limiting** and security headers
- **Environment-based configuration**

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- MongoDB 6.0+
- Docker (optional)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/kani-jayachandran/ChennaiSharks_FedEx.git
cd dca-management-platform
```

2. **Install dependencies**
```bash
# Backend
cd backend
npm install

# Frontend
cd ../frontend
npm install

# AI Services
cd ../fedex
pip install -r requirements.txt
```

3. **Environment Setup**
```bash
# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
cp ai-services/.env.example ai-services/.env
```

4. **Start Services**
```bash
# Start MongoDB (if not using Docker)
mongod

# Start AI Services
cd ai-services
python main.py

# Start Backend
cd ../backend
npm run dev

# Start Frontend
cd ../frontend
npm start
```

5. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- AI Services: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## User Roles & Access

### Admin
- Full system access
- User management
- DCA onboarding
- System configuration
- Advanced analytics

### Enterprise Manager
- Case oversight
- DCA performance monitoring
- Workflow management
- Reporting and analytics
- SLA monitoring

### DCA User
- Assigned case management
- Status updates
- Document uploads
- Communication logs
- Performance metrics

## Key Workflows

### Case Lifecycle
1. **Ingestion** → Cases imported from enterprise systems
2. **AI Analysis** → Recovery probability and priority scoring
3. **Allocation** → Intelligent assignment to optimal DCA
4. **Processing** → DCA works the case through defined states
5. **Monitoring** → SLA tracking and escalation management
6. **Closure** → Final resolution and performance analysis

### SLA Management
- Automated timer initiation on case assignment
- Breach detection and alert generation
- Escalation triggers based on predefined rules
- Performance impact tracking

## Security Features

- **Authentication**: JWT-based with refresh tokens
- **Authorization**: Role-based access control (RBAC)
- **Data Isolation**: Tenant-based data segregation
- **Audit Logging**: Complete action traceability
- **API Security**: Rate limiting, CORS, input validation
- **Encryption**: Data at rest and in transit

## Monitoring & Analytics

### Key Performance Indicators (KPIs)
- **Recovery Rate**: Percentage of successfully recovered cases
- **Average Recovery Time**: Mean time from assignment to closure
- **SLA Compliance**: Percentage of cases meeting SLA requirements
- **DCA Efficiency**: Performance metrics per agency
- **Aging Analysis**: Distribution of cases by overdue periods
- **Predictive Accuracy**: ML model performance metrics

### Dashboard Features
- Real-time metrics updates
- Interactive filtering and drill-down
- Exportable reports
- Customizable views
- Alert notifications

## API Documentation

### Authentication Endpoints
- `POST /api/auth/login` - User authentication
- `POST /api/auth/refresh` - Token refresh
- `POST /api/auth/logout` - User logout

### Case Management
- `GET /api/cases` - List cases with filtering
- `POST /api/cases` - Create new case
- `PUT /api/cases/:id` - Update case
- `GET /api/cases/:id/history` - Case audit trail

### DCA Management
- `GET /api/dcas` - List DCAs
- `POST /api/dcas` - Register new DCA
- `GET /api/dcas/:id/performance` - DCA metrics

### Analytics
- `GET /api/analytics/dashboard` - Dashboard data
- `GET /api/analytics/recovery-trends` - Recovery analysis
- `GET /api/analytics/sla-compliance` - SLA metrics

## Development Guidelines

### Code Standards
- TypeScript for type safety
- ESLint + Prettier for code formatting
- Comprehensive error handling
- Unit and integration testing
- API documentation with OpenAPI/Swagger

### Database Design
- Normalized schema with proper indexing
- Audit trail implementation
- Soft deletes for data retention
- Performance optimization

### Security Best Practices
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF tokens
- Secure headers

## Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Production Considerations
- Environment-specific configurations
- Database backup strategies
- Log aggregation and monitoring
- SSL/TLS certificate management
- Load balancing and scaling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request
5. Code review and merge

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For technical support or questions:
- Create an issue in the repository
- Contact the development team
- Review the documentation wiki

---


**Built for Enterprise Scale | Powered by AI | Secured by Design**
