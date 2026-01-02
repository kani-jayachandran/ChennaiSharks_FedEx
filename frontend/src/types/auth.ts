export interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  role: 'admin' | 'enterprise_manager' | 'dca_user';
  permissions: string[];
  organization?: string;
  department?: string;
  position?: string;
  dcaId?: string;
  phone?: string;
  timezone: string;
  isActive: boolean;
  isEmailVerified: boolean;
  lastLogin?: string;
  lastActivity?: string;
  preferences: {
    notifications: {
      email: boolean;
      sms: boolean;
      push: boolean;
    };
    dashboard: {
      defaultView: 'overview' | 'cases' | 'analytics';
      refreshInterval: number;
    };
    language: string;
    dateFormat: string;
  };
  createdAt: string;
  updatedAt: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  data: {
    user: User;
    token: string;
    refreshToken: string;
  };
}

export interface RegisterRequest {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  role: 'admin' | 'enterprise_manager' | 'dca_user';
  organization?: string;
  department?: string;
  position?: string;
  phone?: string;
  dcaId?: string;
}

export interface RegisterResponse {
  success: boolean;
  message: string;
  data: {
    user: User;
    token: string;
    refreshToken: string;
  };
}

export interface RefreshTokenRequest {
  refreshToken: string;
}

export interface RefreshTokenResponse {
  success: boolean;
  data: {
    token: string;
    refreshToken: string;
  };
}

export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  password: string;
}

export interface UpdateProfileRequest {
  firstName?: string;
  lastName?: string;
  phone?: string;
  timezone?: string;
  preferences?: Partial<User['preferences']>;
}