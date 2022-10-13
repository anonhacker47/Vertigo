import{A as r}from"./index.9a048c99.js";const n={register(e){return r().post("users",e)},login(e){return r().post("tokens",null,e)},refreshToken(e){return r().put("tokens",e)}};export{n as A};
