import { z } from "zod";

export const MessageSchema = z.object({
  id: z.string().uuid(),
  role: z.string(),
  content: z.string(),
  chat_id: z.string().uuid(),
  created_at: z.string().datetime(),
});

export const ChatSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  messages: z.array(MessageSchema),
  created_at: z.string().datetime(),
});

export const ShortChatSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  created_at: z.string().datetime(),
});

export const ChatsListSchema = z.array(ShortChatSchema);

export const SendMessageRequestSchema = z.object({
  chat_id: z.string().uuid().nullable(),
  content: z.string(),
});

export const SendMessageResponseSchema = z.array(MessageSchema);