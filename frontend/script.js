async function askQuestion() {
      const input = document.getElementById("question");
      const chatBox = document.getElementById("chat");
      const question = input.value.trim();
      if (!question) return;

      // Display user's message
      const userMsg = document.createElement("div");
      userMsg.className = "message user";
      userMsg.textContent = question;
      chatBox.appendChild(userMsg);
      input.value = "";

      // Scroll down
      chatBox.scrollTop = chatBox.scrollHeight;

      // Send to backend
      try {
        const res = await fetch("/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question })
        });
        const data = await res.json();

        const botMsg = document.createElement("div");
        botMsg.className = "message bot";
        botMsg.textContent = data.answer;
        chatBox.appendChild(botMsg);
        chatBox.scrollTop = chatBox.scrollHeight;
      } catch (err) {
        const botMsg = document.createElement("div");
        botMsg.className = "message bot";
        botMsg.textContent = "Sorry, something went wrong.";
        chatBox.appendChild(botMsg);
      }
    }