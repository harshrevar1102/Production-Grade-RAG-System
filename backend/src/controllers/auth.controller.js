const authService = require("../services/auth.service");
const { z } = require("zod");

// ==========================================
// VALIDATION SCHEMAS
// ==========================================

const registerSchema = z.object({
  name: z.string().min(2).max(100),
  email: z.string().email(),
  password: z.string().min(8).max(100),
});

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).max(100),
});

const forgotPasswordSchema = z.object({
  email: z.string().email(),
});

const resetPasswordSchema = z.object({
  token: z.string().min(1),
  newPassword: z.string().min(8).max(100),
});

const changePasswordSchema = z.object({
  currentPassword: z.string().min(8).max(100),
  newPassword: z.string().min(8).max(100),
});

// ==========================================
// REGISTER
// ==========================================

const register = async (req, res, next) => {
  try {
    const data = registerSchema.parse(req.body);

    const result = await authService.registerUser(data);

    res.status(201).json({
      success: true,
      message: "User registered successfully",
      data: result,
    });
  } catch (error) {
    next(error);
  }
};

// ==========================================
// LOGIN
// ==========================================

const login = async (req, res, next) => {
  try {
    const data = loginSchema.parse(req.body);

    const result = await authService.loginUser(data);

    res.status(200).json({
      success: true,
      message: "Login successful",
      data: result,
    });
  } catch (error) {
    next(error);
  }
};

// ==========================================
// GET CURRENT USER
// ==========================================

const getMe = async (req, res, next) => {
  try {
    const user = await authService.getCurrentUser(
      req.userId
    );

    res.status(200).json({
      success: true,
      data: {
        user,
      },
    });
  } catch (error) {
    next(error);
  }
};

// ==========================================
// FORGOT PASSWORD
// ==========================================

const forgotPassword = async (req, res, next) => {
  try {
    const { email } =
      forgotPasswordSchema.parse(req.body);

    await authService.forgotPassword(email);

    res.status(200).json({
      success: true,
      message:
        "If an account exists with that email, a password reset link has been sent.",
    });
  } catch (error) {
    next(error);
  }
};

// ==========================================
// RESET PASSWORD
// ==========================================

const resetPassword = async (req, res, next) => {
  try {
    const {
      token,
      newPassword,
    } = resetPasswordSchema.parse(req.body);

    await authService.resetPassword(
      token,
      newPassword
    );

    res.status(200).json({
      success: true,
      message: "Password reset successfully",
    });
  } catch (error) {
    next(error);
  }
};

// ==========================================
// CHANGE PASSWORD
// ==========================================

const changePassword = async (req, res, next) => {
  try {
    const {
      currentPassword,
      newPassword,
    } = changePasswordSchema.parse(req.body);

    await authService.changePassword(
      req.userId,
      currentPassword,
      newPassword
    );

    res.status(200).json({
      success: true,
      message: "Password changed successfully",
    });
  } catch (error) {
    next(error);
  }
};

// ==========================================
// EXPORTS
// ==========================================

module.exports = {
  register,
  login,
  getMe,
  forgotPassword,
  resetPassword,
  changePassword,
};