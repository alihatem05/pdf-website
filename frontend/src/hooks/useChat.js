import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getChat, getChats, sendMessage, deleteChat } from "../api/chat";

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