import { ZodError } from "zod";

export function getErrorMessage(error) {
  if (error instanceof ZodError) {
    return error.issues[0]?.message || "Validation failed";
  }

  if (error?.response?.data?.detail) {
    return error.response.data.detail;
  }

  if (error?.message) {
    return error.message;
  }

  return "Something went wrong. Please try again.";
}
