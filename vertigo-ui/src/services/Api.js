import axios from "axios";

export default () => {
  var axiosInstance = axios.create({
    withCredentials: true,

    baseURL: "http://192.168.18.4:5000/api",
  });

  axiosInstance.interceptors.request.use(
    function (config) {
      // Do something before request is sent

      return config;
    },

    function (error) {
      // Do something with request error

      return Promise.reject(error);
    }
  );

  // Add a response interceptor

  axiosInstance.interceptors.response.use(
    function (response) {
      // Any status code that lie within the range of 2xx cause this function to trigger

      // Do something with response data

      return response;
    },

    function (error) {
      // Any status codes that falls outside the range of 2xx cause this function to trigger
      // Do something with response error
      
      if (error.response.status == 401) {

        const originalConfig = error.config;
        console.log("Token Expired, Refreshing");

        return axiosInstance
          .put("tokens", {
            access_token: localStorage.getItem("token"),
          })
          .then(function (response) {
            localStorage.setItem("token", response.data.access_token);
            originalConfig.headers["Authorization"] =
              "Bearer " + response.data.access_token;
            return axiosInstance(originalConfig);
          })
          .catch(function (err) {
            console.error(err);
          });
        }
        else{
          console.log(error);
        }

        return Promise.reject(error);
      
    }
  );
  return axiosInstance;
};
