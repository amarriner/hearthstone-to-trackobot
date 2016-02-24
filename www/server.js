var express	= require('express')
var app		= express();
var port	= process.env.PORT || 9090;
var fs		= require('fs');
var modeFile	= '/home/amarriner/python/hearthstone-parse/mode';
var rankFile	= '/home/amarriner/python/hearthstone-parse/rank';

if (! process.env.HS_PARSE_SECRET) {
   console.log('Missing HS_PARSE_SECRET environment variable, exiting...');
   return;
}

app.use('/hs-parse', express.static(__dirname + '/static'));

app.get('/hs-parse/api/get-mode', function(req, res) {
   
   return res.status(201).json({ mode: fs.readFileSync(modeFile).toString() });
   
});

app.get('/hs-parse/api/get-rank', function(req, res) {
   
   return res.status(201).json({ rank: fs.readFileSync(rankFile).toString() });
   
});

app.get('/hs-parse/api/set', function(req, res) {

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

   var rank = parseInt(req.query.rank);
   if (! rank) {
      return res.status(404).json({ message: 'ERROR: Invalid rank' });
   }

   if (rank && !(rank < 25 && rank > 0)) {
      return res.status(404).json({ message: 'ERROR: Invalid rank' });
   }

   fs.writeFileSync(modeFile, req.query.mode);
   var message = 'Updated mode to ' + req.query.mode;

   if (req.query.rank) {
      fs.writeFileSync(rankFile, req.query.rank);
      message += ', and rank to ' + req.query.rank;
   }

   return res.status(201).json({ message: message });
});

app.listen(port);
console.log('Server listening on port ' + port);
