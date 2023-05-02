cd "$(dirname "$0")";

open -a Terminal "./pyjengine/run.sh"
open -a Terminal "./bidengine/run.sh"
open -a Terminal "./web-notifier/run.sh"
cd jengine
npm start
