import { z } from "zod";

export const LoginSchema = z.object({
  email: z
    .string()
    .email("Enter a valid email address")
    .min(1, "Email is required")
    .toLowerCase()
    .trim(),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .min(1, "Password is required"),
  remember_me: z.boolean().optional().default(false),
});

export const RegisterSchema = z.object({
  username: z
    .string()
    .min(1, "Username is required")
    .min(3, "Username must be at least 3 characters"),
  email: z
    .string()
    .email("Enter a valid email address")
    .min(1, "Email is required"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .min(1, "Password is required"),
  remember_me: z.boolean().optional().default(false),
});

export const AuthResponseSchema = z.object({
  access_token: z.string(),
  user: z.object({
    id: z.string().optional(),
    email: z.string(),
    username: z.string().optional(),
  }),
});
