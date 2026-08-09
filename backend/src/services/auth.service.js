const crypto = require("crypto");

const prisma = require("../config/prisma");

const {
  hashPassword,
  comparePassword,
} = require("../utils/hash");

const {
  generateToken,
} = require("../utils/jwt");

const {
  sendPasswordResetEmail,
} = require("../utils/email");

// ==========================================
// REGISTER
// ==========================================

const registerUser = async ({
  name,
  email,
  password,
}) => {
  const normalizedEmail = email.toLowerCase().trim();

  const existingUser = await prisma.user.findUnique({
    where: {
      email: normalizedEmail,
    },
  });

  if (existingUser) {
    const error = new Error("User already exists");
    error.statusCode = 409;
    throw error;
  }

  const hashedPassword = await hashPassword(password);

  const user = await prisma.user.create({
    data: {
      name: name.trim(),
      email: normalizedEmail,
      password: hashedPassword,
    },
  });

  const token = generateToken(user.id);

  return {
    user: {
      id: user.id,
      name: user.name,
      email: user.email,
    },
    token,
  };
};

// ==========================================
// LOGIN
// ==========================================

const loginUser = async ({
  email,
  password,
}) => {
  const normalizedEmail = email.toLowerCase().trim();

  const user = await prisma.user.findUnique({
    where: {
      email: normalizedEmail,
    },
  });

  if (!user) {
    const error = new Error(
      "Invalid email or password"
    );

    error.statusCode = 401;
    throw error;
  }

  const validPassword = await comparePassword(
    password,
    user.password
  );

  if (!validPassword) {
    const error = new Error(
      "Invalid email or password"
    );

    error.statusCode = 401;
    throw error;
  }

  const token = generateToken(user.id);

  return {
    user: {
      id: user.id,
      name: user.name,
      email: user.email,
    },
    token,
  };
};

// ==========================================
// GET CURRENT USER
// ==========================================

const getCurrentUser = async (userId) => {
  const user = await prisma.user.findUnique({
    where: {
      id: userId,
    },
    select: {
      id: true,
      name: true,
      email: true,
      createdAt: true,
    },
  });

  if (!user) {
    const error = new Error("User not found");

    error.statusCode = 404;
    throw error;
  }

  return user;
};

// ==========================================
// FORGOT PASSWORD
// ==========================================

const forgotPassword = async (email) => {
  const normalizedEmail = email.toLowerCase().trim();

  const user = await prisma.user.findUnique({
    where: {
      email: normalizedEmail,
    },
  });

  // Don't reveal whether the email exists.
  if (!user) {
    return;
  }

  // Delete old reset tokens.
  await prisma.passwordResetToken.deleteMany({
    where: {
      userId: user.id,
    },
  });

  // Generate secure random token.
  const rawToken = crypto
    .randomBytes(32)
    .toString("hex");

  // Store only token hash in database.
  const tokenHash = crypto
    .createHash("sha256")
    .update(rawToken)
    .digest("hex");

  // Token expires after 15 minutes.
  const expiresAt = new Date(
    Date.now() + 15 * 60 * 1000
  );

  await prisma.passwordResetToken.create({
    data: {
      tokenHash,
      userId: user.id,
      expiresAt,
    },
  });

  const resetUrl =
    `${process.env.FRONTEND_URL}/reset-password?token=${rawToken}`;

  await sendPasswordResetEmail(
    user.email,
    resetUrl
  );
};

// ==========================================
// RESET PASSWORD
// ==========================================

const resetPassword = async (
  token,
  newPassword
) => {
  const tokenHash = crypto
    .createHash("sha256")
    .update(token)
    .digest("hex");

  const resetToken =
    await prisma.passwordResetToken.findUnique({
      where: {
        tokenHash,
      },
    });

  if (!resetToken) {
    const error = new Error(
      "Invalid or expired reset token"
    );

    error.statusCode = 400;
    throw error;
  }

  if (resetToken.expiresAt < new Date()) {
    await prisma.passwordResetToken.delete({
      where: {
        id: resetToken.id,
      },
    });

    const error = new Error(
      "Invalid or expired reset token"
    );

    error.statusCode = 400;
    throw error;
  }

  const hashedPassword =
    await hashPassword(newPassword);

  await prisma.$transaction([
    prisma.user.update({
      where: {
        id: resetToken.userId,
      },
      data: {
        password: hashedPassword,
      },
    }),

    // Make token single-use.
    prisma.passwordResetToken.delete({
      where: {
        id: resetToken.id,
      },
    }),

    // Remove any other reset tokens.
    prisma.passwordResetToken.deleteMany({
      where: {
        userId: resetToken.userId,
      },
    }),
  ]);
};

// ==========================================
// CHANGE PASSWORD
// ==========================================

const changePassword = async (
  userId,
  currentPassword,
  newPassword
) => {
  const user = await prisma.user.findUnique({
    where: {
      id: userId,
    },
  });

  if (!user) {
    const error = new Error("User not found");

    error.statusCode = 404;
    throw error;
  }

  const isCurrentPasswordValid =
    await comparePassword(
      currentPassword,
      user.password
    );

  if (!isCurrentPasswordValid) {
    const error = new Error(
      "Current password is incorrect"
    );

    error.statusCode = 401;
    throw error;
  }

  if (currentPassword === newPassword) {
    const error = new Error(
      "New password must be different from current password"
    );

    error.statusCode = 400;
    throw error;
  }

  const hashedPassword =
    await hashPassword(newPassword);

  await prisma.user.update({
    where: {
      id: userId,
    },
    data: {
      password: hashedPassword,
    },
  });
};

// ==========================================
// EXPORTS
// ==========================================

module.exports = {
  registerUser,
  loginUser,
  getCurrentUser,
  forgotPassword,
  resetPassword,
  changePassword,
};