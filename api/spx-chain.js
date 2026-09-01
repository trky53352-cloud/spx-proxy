export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET");

  const TOKEN = "OFBBWEVfdkM4cHlxS0N6cm9GUzhyYWtVVlZVLUxNb1d6QUYtWmlLTW1nbz0";
  const underlying = req.query.underlying || "SPX";

  try {
    const url = "https://api.marketdata.app/v1/options/chain/" + underlying + "/?token=" + TOKEN;
    const response = await fetch(url);
    const data = await response.json();
    res.status(200).json(data);
  } catch (err) {
    res.status(500).json({ s: "error", errmsg: err.message });
  }
}
