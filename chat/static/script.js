document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chat-box");
  const userInput = document.getElementById("user-input");
  const sendButton = document.getElementById("send-button");
  const searchButton = document.getElementById("search-button");
  const removeButton = document.getElementById("remove-button");

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

  function addReceiptToChat(receipt, arquivo) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", "bot");

    const messageContentDiv = document.createElement("div");
    messageContentDiv.classList.add("message-content");
    messageContentDiv.textContent = `${receipt}: `;

    const downloadContentDiv = document.createElement("a");
    downloadContentDiv.href = `/receitas/${arquivo}`;
    downloadContentDiv.download = true;
    downloadContentDiv.textContent = "Download ⬇️";

    messageContentDiv.appendChild(downloadContentDiv);
    messageDiv.appendChild(messageContentDiv);
    chatBox.appendChild(messageDiv);
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
      const content = await fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ "pergunta": userMessage }),
        credentials: 'include'
      });

      const data = await content.json();

      if (data.receitas && data.receitas.length > 0) {
        addMessageToChat("Essas são as receitas que mais alinham com sua necessidade:", "bot");
        for (const receita of data.receitas) {
          addReceiptToChat(`${receita.titulo}`, receita.arquivo);
        }
      } 
      addMessageToChat(data.resposta, "bot");
      
    } catch (error) {
      addMessageToChat(`Falha na comunicação: ${error.message}`, "bot");
    }
  }

  async function searchReceipts(tipo) {
    try {
      const content = await fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ "pergunta": "iniciar pesquisa", "tipo": tipo }),
      });

      const data = await content.json();
      addMessageToChat(data.resposta, "bot");
    } catch (error) {
      print(`Erro ao iniciar pesquisa: ${error.message}`);
    }
  }

  sendButton.addEventListener("click", handleUserMessage);

  userInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      handleUserMessage();
    }
  });

  searchButton.addEventListener("click", () => searchReceipts("com_ingredientes"))
  removeButton.addEventListener("click", () => searchReceipts("sem_ingredientes"))
});
