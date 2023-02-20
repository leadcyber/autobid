const axios = require('axios')
const { SocksProxyAgent } = require("socks-proxy-agent")

const httpsAgent = new SocksProxyAgent({
  hostname: "54.158.238.41",
  port: 69,
  // type: 5,
  userId: "dante",
  password: "j85h8di"
})
const myAxios = axios.create({httpsAgent})
myAxios.get("https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search").then(res => {
  console.log(res)
}).catch(err => {
  console.log(err)
})
