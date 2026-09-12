import { z } from "zod";

export const MessageSchema = z.object({
  id: z.string().uuid(),
  role: z.string(),
  content: z.string(),
  chat_id: z.string().uuid(),
  created_at: z.string().datetime({ offset: true }),
});

export const DocumentSchema = z.object({
  id: z.string().uuid(),
  filename: z.string(),
  status: z.string(),
  error_message: z.string().nullable().optional(),
  created_at: z.string().datetime({ offset: true }),
});

export const ChatSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  messages: z.array(MessageSchema),
  documents: z.array(DocumentSchema).default([]),
  created_at: z.string().datetime({ offset: true }),
});

export const ShortChatSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  created_at: z.string().datetime({ offset: true }),
});

export const ChatsListSchema = z.array(ShortChatSchema);

export const SendMessageRequestSchema = z.object({
  chat_id: z.string().uuid().nullable(),
  content: z.string(),
});

export const SendMessageResponseSchema = z.array(MessageSchema);