<template>
  <div class="main-body app sidebar-mini">
    <!-- Loader -->
    <div id="global-loader">
      <img src="../assets/img/loader.svg" class="loader-img" alt="Loader" />
    </div>
    <!-- /Loader -->

    <!-- Page -->
    <div class="page">
      <div class="main-content app-content">
        <div class="container-fluid">
          <div class="row main-content-app mb-4 mt-5">
            <div class="col-xl-8 col-lg-7 mt-5">
              <div class="card mt-5">
                <a class="main-header-arrow" href="#" id="ChatBodyHide">
                  <i class="icon ion-md-arrow-back"></i>
                </a>
                <div class="main-content-body">
                  <div class="main-chat-header">
                    <div class="main-img-user">
                      <img alt="" src="/src/assets/img/faces/bot2.avif" />
                    </div>
                    <div class="main-chat-msg-name">
                      <h6>Mombasa County Robo</h6>
                      <small>Online</small>
                    </div>
                  </div>
                  <!-- main-chat-header -->
                  <div
                    class="main-chat-body overflow-auto"
                    id="ChatBody"
                    ref="chatBody"
                  >
                    <div class="content-inner">
                      <div
                        v-for="(message, index) in messages"
                        :key="index"
                        class="media"
                        :class="{
                          'flex-row-reverse': message.sender === 'user',
                        }"
                      >
                        <div
                          class="main-img-user"
                          :class="{ online: message.sender === 'user' }"
                        >
                          <img
                            :src="
                              message.sender === 'user'
                                ? '../src/assets/img/faces/9.jpg'
                                : '../src/assets/img/faces/bot.avif'
                            "
                            alt=""
                          />
                        </div>
                        <div class="media-body">
                          <div
                            class="main-msg-wrapper"
                            :class="{
                              right: message.sender === 'user',
                              left: message.sender !== 'user',
                            }"
                          >
                            <span
                              v-if="message.sender === 'bot'"
                              v-html="message.text"
                            ></span>
                            <span v-else>{{ message.text }}</span>
                          </div>
                          <div>
                            <span>{{
                              new Date().toLocaleTimeString([], {
                                hour: "2-digit",
                                minute: "2-digit",
                              })
                            }}</span>
                            <a href="#"
                              ><i class="icon ion-android-more-horizontal"></i
                            ></a>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="main-chat-footer">
                  <input
                    class="form-control"
                    v-model="userMessage"
                    placeholder="Type your message here..."
                    type="text"
                    @keyup.enter="sendMessage"
                  />
                  <a class="main-msg-send" @click="sendMessage">
                    <i class="far fa-paper-plane"></i>
                  </a>
                </div>
              </div>
            </div>
          </div>
          <!-- row -->
        </div>
        <!-- Container closed -->
      </div>
      <!-- main-content closed -->
      <div class="main-footer ht-40">
        <div class="container-fluid pd-t-0-f ht-100p">
          <span
            >Copyright © 2021 <a href="#">Valex</a>. Designed by
            <a href="https://www.spruko.com/">Spruko</a> All rights
            reserved.</span
          >
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      userMessage: "", // User input message
      messages: [], // Array to hold chat messages
    };
  },
  methods: {
    sendMessage() {
      const message = this.userMessage.trim(); // Trim whitespace
      if (message) {
        // Add user message to the chat
        this.messages.push({ sender: "user", text: message });

        // Send message to backend
        axios
          .post("http://127.0.0.1:5000/chat", { message })
          .then((response) => {
            if (response.data && response.data.response) {
              this.messages.push({
                sender: "bot",
                text: response.data.response,
              });
              this.$nextTick(() => {
                const chatBody = this.$refs.chatBody;
                chatBody.scrollTop = chatBody.scrollHeight;
              });
            } else {
              console.error("Unexpected response structure:", response.data);
            }
          })
          .catch((error) => {
            console.error(
              "There was an error with the request:",
              error.response ? error.response.data : error.message
            );
          });

        this.userMessage = "";
        this.$nextTick(() => {
          const chatBody = this.$refs.chatBody;
          chatBody.scrollTop = chatBody.scrollHeight;
        });
      }
    },
  },
};
</script>

<style scoped>
.main-content-body {
  width: 100%; /* Make sure this is wide enough */
}

.card {
  width: 150%; /* Ensure the card takes the full width of the parent */
  max-width: 800px; /* Set a max width if necessary */
  margin: 0 auto; /* Center the card */
}

.main-chat-body {
  width: 90% !important; /* Enforce this width */
  height: 400px; /* Adjust the height as needed */
  overflow-y: auto; /* Ensure vertical scrolling if content overflows */
  margin: 0 auto; /* Center the chat window */
}
</style>
