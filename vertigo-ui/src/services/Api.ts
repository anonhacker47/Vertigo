import axios from "axios";
import router from "../router";

export default () => {
  const axiosInstance = axios.create({
    baseURL: `${import.meta.env.VITE_Base_URL}/api`,
    withCredentials: false,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });

  const refreshAxiosInstance = axios.create({
    baseURL: `${import.meta.env.VITE_Base_URL}/api`,
    withCredentials: true,
  });

  axiosInstance.interceptors.request.use((config) => {
    return config;
  });

  axiosInstance.interceptors.response.use(
    (response) => {
      return response;
    },
    async (error) => {
      const originalRequest = error.config;

      if (error.response?.status === 401 && originalRequest.url != "tokens") {
        try {
          const token = localStorage.getItem("token");

          const response = await refreshAxiosInstance.put("tokens", {
            access_token: token,
          });

          if (response.data.access_token) {
            const newToken = response.data.access_token;

            originalRequest.headers["Authorization"] = "Bearer " + newToken;

            localStorage.setItem("token", newToken);

            return await axiosInstance(originalRequest);
          }
        } catch (error) {
          localStorage.clear();
          router.push("/login");
          return Promise.reject(error as Error);
        }
      }

      return Promise.reject(error as Error);
    }
  );

  return axiosInstance;
};
