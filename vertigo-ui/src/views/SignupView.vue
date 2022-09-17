<template>
   <div class="flex justify-center items-center h-screen">
  <PanelCardItem>
    <h1
      class="text-xl font-bold leading-tight tracking-tight text-gray-900 md:text-2xl dark:text-white"
    >
      Create your Vertigo Account
    </h1>
    <FormKit type="form" submit-label="Sign up" @submit="register">
      <FormKit
        type="text"
        name="username"
        label="Username"
        validation="required"
      />
      <FormKit
        type="email"
        name="email"
        label="Email Address"
        validation="required|email|"
        placeholder="demo@company.com"
      />
      <FormKit
        type="password"
        name="password"
        label="Password"
        validation="required"
      />
      <FormKit
        type="password"
        name="password_confirm"
        label="Confirm Password"
        validation="required|confirm"
        validation-label="Password confirmation"
      />
      <h1 v-if="message != ''" class="error py-5">{{ message }}</h1>
    </FormKit></PanelCardItem></div>
</template>

<script setup>
import { ref } from "vue";
import AuthenticationService from "../services/AuthenticationService";
import PanelCardItem from "../components/cards/PanelCardItem.vue"

let username = ref("");
let email = ref("");
let password = ref("");
const message = ref('');

// function submitHandler(values) {
//     //do something with the form data
//     username=values.username;
//     email_id=values.email_id;
//     password=values.email_id;
//     console.log(values);

//   }

async function register(values) {
  try {
    const response = await AuthenticationService.register({
      username: values.username,
      email: values.email,
      password: values.password,
    });
  } catch (error) {
    message.value = error.response.data.errors;
  }
  console.log(message);
}
</script>

<style>
.formkit-outer {
  color: white;
  outline: none m !important;
}

.formkit-inner {
  background-color: #404a59;
  color: white;
  outline: none m !important;
  box-shadow: 0 0 0 1px #1f2937;
}

[data-type="button"] .formkit-input,
[data-type="submit"] .formkit-input {
  width: 100%;
}
.error {
  color: red;
}
</style>
