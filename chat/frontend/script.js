document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chat-box");
  const userInput = document.getElementById("user-input");
  const sendButton = document.getElementById("send-button");
  const searchButton = document.getElementById("search-button");

  function addMessageToChat(message, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);

    const messageContentDiv = document.createElement("div");
    messageContentDiv.classList.add("message-content");
    messageContentDiv.textContent = message;

    messageDiv.appendChild(messageContentDiv);
    chatBox.appendChild(messageDiv);

    // Rolagem automática para a última mensagem
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function handleUserMessage() {
    const messageText = userInput.value.trim();
    if (messageText === "") {
      return;
    }

    addMessageToChat(messageText, "user");
    userInput.value = "";

    sendMessage(messageText);
  }

  async function sendMessage(userMessage) {
    addMessageToChat("Digitando...", "bot-typing");

    const botDigitando = chatBox.querySelector(".bot-typing");
    if (botDigitando) {
      botDigitando.remove();
    }

    try {
      const content = await fetch("http://127.0.0.1:5001/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ "pergunta": userMessage }),
      });

      const data = await content.json();

      addMessageToChat(data.response["resposta"], "bot");
    } catch (error) {
      addMessageToChat(`Falha na comunicação: ${error.message}`, "bot");
    }
  }

  async function searchReceipts() {
    try {
      const content = await fetch("http://127.0.0.1:5001/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ "pergunta": "iniciar pesquisa" }),
      });

      const data = await content.json();
      addMessageToChat(data.response["resposta"], "bot");
    } catch (error) {
      print(`Erro ao iniciar pesquisa: ${error.message}`);
    }
  }

  // Event Listeners
  sendButton.addEventListener("click", handleUserMessage);

  userInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      handleUserMessage();
    }
  });

  searchButton.addEventListener("click", searchReceipts)
});
