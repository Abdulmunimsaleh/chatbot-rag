<template>
  <div class="main-body app sidebar-mini">
    <!-- Loader -->
    <div id="global-loader" v-if="loading">
      <img src="../assets/img/loader.svg" class="loader-img" alt="Loader" />
    </div>
    <!-- /Loader -->

    <!-- Page -->
    <div class="page">
      <div class="main-content app-content">
        <div class="container-fluid">
          <div class="row main-content-app mb-4 mt-5">
            <div class="col-xl-6 col-lg-6 mt-5">
              <div class="card d-flex flex-wrap">
                <div class="card-body">
                  <h6 class="card-title mb-1">File Upload</h6>
                  <input
                    type="file"
                    class="dropify"
                    data-height="200"
                    @change="handleFileUpload"
                  />
                  <textarea
                    class="form-control mt-3"
                    placeholder="File Summary Contents"
                    rows="5"
                  ></textarea>
                  <button
                    type="submit"
                    class="btn btn-primary mt-4"
                    @click="submitFile"
                  >
                    Submit
                  </button>
                  <h6 class="card-title mt-4">TXT BASE64</h6>
                  <textarea
                    class="form-control"
                    placeholder="Base64 encoded text will appear here"
                    rows="10"
                    v-model="base64Text"
                    readonly
                  ></textarea>
                </div>
              </div>
            </div>

            <div
              class="select-option"
              style="position: absolute; top: 10px; right: 10px"
            >
              <h6 class="card-title mb-1">Select Option</h6>
              <div>
                <button class="btn btn-primary" @click="showSection('upload')">
                  File Upload
                </button>
                <span style="margin: 0 20px"></span>
                <button class="btn btn-primary" @click="showSection('chat')">
                  Chat
                </button>
              </div>
            </div>

            <div class="col-xl-6 col-lg-6 mt-5">
              <div class="card mt-5">
                <div class="main-content-body">
                  <div v-if="activeSection === 'chat'" class="mt-5 pt-4">
                    <div class="main-chat-header">
                      <div class="main-img-user">
                        <img alt="" src="/src/assets/img/faces/bot2.avif" />
                      </div>
                      <div class="main-chat-msg-name">
                        <h6>Mombasa County Robo</h6>
                        <small>Online</small>
                      </div>
                    </div>
                    <div class="main-chat-body overflow-auto" ref="chatBody">
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
            </div>
          </div>
          <!-- row closed -->
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
      <!-- Footer closed -->
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      messages: [],
      userMessage: "",
      base64Text: "",
      activeSection: "upload", // Default active section
      uploadedFile: null, // Store the uploaded file
      loading: false,
    };
  },
  methods: {
    showSection(section) {
      this.activeSection = section; // Change the active section
    },
    sendMessage() {
      if (this.userMessage.trim() !== "") {
        this.messages.push({ sender: "user", text: this.userMessage });

        fetch("http://localhost:5000/ask", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ question: this.userMessage }),
        })
          .then((response) => {
            if (!response.ok) throw new Error("Error fetching answer");
            return response.json();
          })
          .then((data) => {
            this.messages.push({
              sender: "bot",
              text: data.answer || "Sorry, I don't know the answer.",
            });
          })
          .catch((error) => {
            this.messages.push({ sender: "bot", text: "An error occurred." });
          });

        this.userMessage = "";
      }
    },
    handleFileUpload(event) {
      this.uploadedFile = event.target.files[0]; // Store the uploaded file
      if (this.uploadedFile) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.base64Text = e.target.result; // Update base64Text with the file content
        };
        reader.readAsDataURL(this.uploadedFile);
      }
    },
    submitFile() {
      if (this.uploadedFile) {
        const formData = new FormData();
        formData.append("file", this.uploadedFile);

        this.loading = true; // Show loader

        fetch("http://localhost:5000/upload", {
          method: "POST",
          body: formData,
        })
          .then((response) => {
            if (!response.ok) throw new Error("Error uploading file");
            return response.json();
          })
          .then((data) => {
            console.log(data.message);
            alert(data.message); // Alert the user about successful upload
          })
          .catch((error) => {
            alert(error);
          })
          .finally(() => {
            this.loading = false; // Hide loader
          });
      } else {
        alert("Please upload a file first.");
      }
    },
  },
};
</script>

<style scoped>
.select-option {
  position: absolute;
  top: 20px;
  right: 20px;
}
</style>
