export default async function handler(req, res) {
)CORS يحل مشكلة( يسمح بالوصول من أي موقع //
res.setHeader('Access-Control-Allow-Origin', '*');
res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
if (req.method === 'OPTIONS') {
return res.status(200).end();
}
const underlying = req.query.underlying || 'SPX';
غﻴّر التاريخ ﻷقرب انتهاء تبيه // ;'18-09-2026' || const expiration = req.query.expiration
const strikeLimit = req.query.strikeLimit || '7';
في Environment Variables مفتاحك محفوظ في // ;const token = process.env.MARKETDATA_TOKEN
Vercel
const url = `https://api.marketdata.app/v1/options/chain/${underlying}/?
expiration=${expiration}&strikeLimit=${strikeLimit}`;
try {
const response = await fetch(url, {
headers: {
Authorization: `Bearer ${token}`
}
;)}
if (!response.ok) {
return res.status(response.status).json({
error: true,
message: `MarketData.app returned status ${response.status}`
;)}
}
const data = await response.json();
return res.status(200).json(data);
} catch (err) {
return res.status(500).json({
error: true,
message: err.message
;)}
}
}
