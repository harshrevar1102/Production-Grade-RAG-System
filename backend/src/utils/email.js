const nodemailer = require("nodemailer");

const sendPasswordResetEmail = async (
  email,
  resetUrl
) => {
  // Development mode:
  // If SMTP isn't configured, print the reset URL
  // in the backend terminal.
  if (
    !process.env.SMTP_HOST ||
    !process.env.SMTP_USER ||
    !process.env.SMTP_PASSWORD
  ) {
    console.log(
      "\n========================================"
    );
    console.log("PASSWORD RESET URL");
    console.log(resetUrl);
    console.log(
      "========================================\n"
    );

    return;
  }

  const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: Number(process.env.SMTP_PORT || 587),
    secure: Number(process.env.SMTP_PORT) === 465,

    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASSWORD,
    },
  });

  await transporter.sendMail({
    from:
      process.env.SMTP_FROM ||
      process.env.SMTP_USER,

    to: email,

    subject: "Reset your password",

    text: `Reset your password using this link: ${resetUrl}`,

    html: `
      <div style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2>Reset Your Password</h2>

        <p>
          We received a request to reset your password.
        </p>

        <p>
          Click the button below to reset your password:
        </p>

        <p>
          <a
            href="${resetUrl}"
            style="
              display: inline-block;
              padding: 10px 20px;
              background-color: #007bff;
              color: #ffffff;
              text-decoration: none;
              border-radius: 5px;
            "
          >
            Reset Password
          </a>
        </p>

        <p>
          This link will expire in 15 minutes.
        </p>

        <p>
          If you did not request a password reset,
          you can safely ignore this email.
        </p>
      </div>
    `,
  });
};

module.exports = {
  sendPasswordResetEmail,
};