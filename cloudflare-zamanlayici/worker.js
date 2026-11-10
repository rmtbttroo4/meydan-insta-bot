// MEYDAN GSM Instagram zamanlayicisi (Cloudflare Worker)
// Her gun tam saatinde GitHub'daki "Gunluk Instagram paylasimi" isini baslatir.
// Cron Triggers (UTC, Turkiye = UTC+3):
//   58 6 * * *   -> 09:58 TR -> gunluk Story (10:00'da yayinda)
//   58 8 * * *   -> 11:58 TR -> ogle gonderisi (12:00'de yayinda)
//   56 15 * * *  -> 18:56 TR -> aksam Reels'i  (19:00'da yayinda)
// Gerekli gizli degisken: GH_TOKEN (sadece bu depoda "Actions: Read and write" izinli GitHub token'i)

const REPO = "rmtbttroo4/meydan-insta-bot";
const WORKFLOW = "daily.yml";

async function trigger(env, slot) {
  const r = await fetch(`https://api.github.com/repos/${REPO}/actions/workflows/${WORKFLOW}/dispatches`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.GH_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "meydangsm-insta-zamanlayici",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ ref: "main", inputs: { slot, mod: "paylas" } }),
  });
  if (r.status !== 204) {
    throw new Error(`GitHub tetikleme hatasi ${r.status}: ${(await r.text()).slice(0, 300)}`);
  }
  console.log(`Tetiklendi: ${slot}`);
}

export default {
  async scheduled(event, env, ctx) {
    const slot = event.cron.startsWith("58 6") ? "story" : event.cron.startsWith("58 8") ? "ogle" : "aksam";
    ctx.waitUntil(trigger(env, slot));
  },
  async fetch() {
    return new Response("MEYDAN GSM Instagram zamanlayicisi calisiyor.", {
      headers: { "content-type": "text/plain; charset=utf-8" },
    });
  },
};
