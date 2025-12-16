import{a as r}from"./client-CIWp8brx.js";const o={async getTopScores(e=0,a=20){return(await r.get("/leaderboard/top",{params:{page:e,size:a}})).data},async submitScore(e){return(await r.post("/leaderboard/submit",e)).data},async getUserRank(e){return(await r.get(`/leaderboard/rank/${e}`)).data}};export{o as l};
//# sourceMappingURL=leaderboard-CE2hxYMA.js.map
