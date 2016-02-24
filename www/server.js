var express	= require('express')
var app		= express();
var port	= process.env.PORT || 9090;
var fs		= require('fs');
var file	= '/home/amarriner/python/hearthstone-parse/mode';

if (! process.env.HS_PARSE_SECRET) {
   console.log('Missing HS_PARSE_SECRET environment variable, exiting...');
   return;
}

console.log(__dirname);
app.use('/hs-parse', express.static(__dirname + '/static'));

app.get('/hs-parse/api/get-mode', function(req, res) {
   
   return res.status(201).json({ mode: fs.readFileSync(file).toString() });
   
});

app.get('/hs-parse/api/set-mode', function(req, res) {

   if (! req.query.t) {
      return res.status(404).json({ message: 'ERROR: Missing token' });
   }

   if (req.query.t != process.env.HS_PARSE_SECRET) {
      return res.status(404).json({ message: 'ERROR: Invalid token' });
   }

   if (! req.query.mode) {
      return res.status(404).json({ message: 'ERROR: Missing mode' });
   }

   if (['tavernbrawl', 'casual', 'ranked', 'arena', 'friendly'].indexOf(req.query.mode) <= 0) {
      return res.status(404).json({ message: 'ERROR: Invalid mode' });
   }

   fs.writeFileSync(file, req.query.mode);

   return res.status(201).json({ message: 'Updated mode to ' + req.query.mode });
});

app.listen(port);
console.log('Server listening on port ' + port);
