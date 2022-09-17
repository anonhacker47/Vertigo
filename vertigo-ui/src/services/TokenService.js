import { useUserStore } from "../store/user";

export default{
getToken() {
  const userStore = useUserStore();
  const token = userStore.token;
  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`
  }
  return headers;
}
}