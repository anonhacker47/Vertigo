import{_ as o,o as n,a,b as c,e as d,U as i,A as s}from"./index.3f8611ae.js";const l={},_={class:"rounded-lg shadow bg-gray-800 border border-gray-700"},u={class:"p-6 space-y-4 sm:p-8"};function p(e,t){return n(),a("div",_,[c("div",u,[d(e.$slots,"default",{},()=>[i(" add something ")])])])}const m=o(l,[["render",p]]),f={register(e){return s().post("users",e)},login(e,t){const r={Authorization:`Basic ${btoa(e+":"+t)}`};return s().post("tokens",null,{headers:r})},getUser(e){return s().get("me",e)},refreshToken(e){return s().put("tokens",e)}};export{f as A,m as P};