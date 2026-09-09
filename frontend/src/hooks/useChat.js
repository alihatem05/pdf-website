import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getChat, getChats, sendMessage, createChatWithDocument, deleteChat } from "../api/chat";

export function useGetChats() {
  return useQuery({
    queryKey: ["chats"],
    queryFn: getChats,
  });
}

export function useGetChat(chatId) {
  return useQuery({
    queryKey: ["chats", chatId],
    queryFn: () => getChat(chatId),
    enabled: !!chatId,
    refetchInterval: (query) =>
      query.state.data?.documents?.some((document) => document.status === "processing") ? 2000 : false,
  });
}

export function useSendMessage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: sendMessage,
    onSuccess: (messages) => {
      const chatId = messages[0]?.chat_id;
      queryClient.invalidateQueries({ queryKey: ["chats"] });
      if (chatId) {
        queryClient.invalidateQueries({ queryKey: ["chats", chatId] });
      }
    },
  });
}

export function useCreateChatWithDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createChatWithDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chats"] });
    },
  });
}

export function useDeleteChat() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteChat,
    onSuccess: (_, chatId) => {
      queryClient.invalidateQueries({ queryKey: ["chats"] });
      if (chatId) {
        queryClient.invalidateQueries({ queryKey: ["chats", chatId] });
      }
    },
  });
}