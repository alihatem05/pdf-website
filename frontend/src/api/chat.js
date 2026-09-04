import api from "./axios";
import { ChatSchema, ChatsListSchema, SendMessageRequestSchema, SendMessageResponseSchema } from "../schemas/chat";
import { getErrorMessage } from "../utils/errorHandler";

export async function getChat(chatId) {
  try {
    const response = await api.get(`/chats/${chatId}`);
    return ChatSchema.parse(response.data);
  } catch (error) {
    const message = getErrorMessage(error);
    const err = new Error(message);
    err.originalError = error;
    throw err;
  }
}

export async function getChats() {
  try {
    const response = await api.get("/chats");
    return ChatsListSchema.parse(response.data);
  } catch (error) {
    const message = getErrorMessage(error);
    const err = new Error(message);
    err.originalError = error;
    throw err;
  }
}

export async function sendMessage({ chatId, content }) {
  try {
    const validated = SendMessageRequestSchema.parse({ chat_id: chatId ?? null, content });
    const response = await api.post("/chats/messages", validated);
    return SendMessageResponseSchema.parse(response.data);
  } catch (error) {
    const message = getErrorMessage(error);
    const err = new Error(message);
    err.originalError = error;
    throw err;
  }
}