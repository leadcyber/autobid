import { connectEmailDB, disconnectEmailDB } from './db';
import { sync, authenticateGmail } from './email/sync'
import { workspacePath } from './config';

const credentialFilePath = `${workspacePath}/email/client_secret_594838840696-46892s5m1p8g8tul7rscavcegm1hk79n.apps.googleusercontent.com.json`;
const cachedCredentialPath = `${workspacePath}/email/mikchielli.cache.json`;

(async () => {
    console.log("Authorizing")
    const client = await authenticateGmail(credentialFilePath, cachedCredentialPath)
    console.log("Successfully authorized.")
    try {
      await connectEmailDB()
      console.log("DB connected")
      console.log("Start sync ...")
      await sync(client)
      await disconnectEmailDB()
    } catch(err) {
      console.log(err)
    }
})()
