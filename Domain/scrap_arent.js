const puppeteer = require('puppeteer');
const fs = require('fs');

// Create a logger function
function log(message) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${message}`;
    console.log(message);
    fs.appendFileSync('log_domain_arent.txt', logMessage + '\n', { encoding: 'utf-8' });
}

// Generate all possible 3-letter combinations (aaa to zzz)
function generateDomainCombinations() {
    const combinations = [];

    // Add 3-letter combinations (aaa to zzz)
    //   for (let i = 0; i < 26; i++) {
    //     for (let j = 0; j < 26; j++) {
    //       for (let k = 0; k < 26; k++) {
    //         const letter1 = String.fromCharCode(97 + i); // a-z
    //         const letter2 = String.fromCharCode(97 + j); // a-z
    //         const letter3 = String.fromCharCode(97 + k); // a-z
    //         combinations.push(`${letter1}${letter2}${letter3}.top`);
    //       }
    //     }
    //   }

    // Add URL shortener domain names (500 suggestions)
    const urlShortenerNames = [
        'go', 'link', 'short', 'url', 'shorten', 'tiny', 'bit', 'cut', 'quick', 'fast',
        'jump', 'hop', 'zip', 'snap', 'dash', 'flash', 'bolt', 'zoom', 'rush', 'speed',
        'rapid', 'swift', 'swift', 'quick', 'fast', 'snap', 'ping', 'pong', 'buzz', 'click',
        'tap', 'hit', 'touch', 'grab', 'catch', 'take', 'get', 'fetch', 'pull', 'push',
        'share', 'send', 'pass', 'give', 'move', 'flow', 'route', 'path', 'lane', 'way',
        'trail', 'track', 'trace', 'follow', 'track', 'mark', 'sign', 'note', 'memo', 'list',
        'nav', 'go2', 'to', 'via', 'at', 'by', 'on', 'up', 'down', 'over',
        'under', 'through', 'across', 'along', 'into', 'out', 'off', 'away', 'back', 'here',
        'there', 'where', 'when', 'now', 'then', 'soon', 'later', 'next', 'fast', 'slow',
        'quick', 'easy', 'simple', 'basic', 'plain', 'clear', 'bright', 'light', 'dark', 'black',
        'white', 'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'gray', 'brown',
        'gold', 'silver', 'bronze', 'copper', 'iron', 'steel', 'glass', 'stone', 'wood', 'metal',
        'smart', 'wise', 'clever', 'bright', 'sharp', 'keen', 'quick', 'swift', 'fast', 'rapid',
        'ultra', 'super', 'mega', 'max', 'pro', 'plus', 'extra', 'more', 'less', 'few',
        'many', 'most', 'best', 'top', 'first', 'last', 'next', 'prev', 'new', 'old',
        'recent', 'latest', 'fresh', 'hot', 'cool', 'warm', 'cold', 'cold', 'nice', 'good',
        'great', 'awesome', 'epic', 'amazing', 'super', 'wonder', 'magic', 'mystic', 'cosmic', 'lunar',
        'solar', 'star', 'moon', 'sun', 'sky', 'cloud', 'rain', 'snow', 'storm', 'wind',
        'air', 'water', 'fire', 'earth', 'nature', 'wild', 'free', 'open', 'wide', 'broad',
        'deep', 'high', 'tall', 'short', 'long', 'small', 'big', 'huge', 'tiny', 'mini',
        'micro', 'nano', 'pico', 'mega', 'giga', 'tera', 'kilo', 'hecto', 'deca', 'deci',
        'centi', 'milli', 'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
        'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma',
        'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega', 'prime', 'zero', 'one', 'two',
        'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'hundred', 'thousand',
        'million', 'billion', 'trillion', 'count', 'number', 'digit', 'code', 'key', 'lock', 'open',
        'close', 'begin', 'start', 'end', 'stop', 'pause', 'play', 'run', 'walk', 'jump',
        'fly', 'swim', 'dive', 'climb', 'crawl', 'move', 'shift', 'turn', 'spin', 'roll',
        'slide', 'slip', 'glide', 'drift', 'float', 'sink', 'rise', 'fall', 'drop', 'bounce',
        'spring', 'leap', 'bound', 'hop', 'skip', 'step', 'pace', 'stride', 'walk', 'stroll',
        'march', 'parade', 'race', 'dash', 'sprint', 'gallop', 'trot', 'canter', 'charge', 'attack',
        'defend', 'protect', 'guard', 'watch', 'see', 'look', 'view', 'observe', 'notice', 'spot',
        'find', 'search', 'seek', 'hunt', 'track', 'trace', 'follow', 'lead', 'guide', 'direct',
        'point', 'show', 'tell', 'speak', 'talk', 'say', 'shout', 'whisper', 'sing', 'sound',
        'hear', 'listen', 'echo', 'ring', 'bell', 'chime', 'tone', 'note', 'tune', 'music',
        'beat', 'rhythm', 'tempo', 'pace', 'speed', 'velocity', 'acceleration', 'force', 'power', 'energy',
        'strength', 'might', 'power', 'vigor', 'vital', 'live', 'alive', 'quick', 'lively', 'active',
        'dynamic', 'static', 'stable', 'steady', 'strong', 'weak', 'soft', 'hard', 'tough', 'fragile',
        'breakable', 'unbreakable', 'flexible', 'rigid', 'elastic', 'plastic', 'fluid', 'liquid', 'solid', 'gas',
        'plasma', 'matter', 'form', 'shape', 'size', 'volume', 'weight', 'mass', 'density', 'light',
        'heavy', 'dense', 'thin', 'thick', 'wide', 'narrow', 'tall', 'short', 'long', 'brief',
        'vast', 'huge', 'enormous', 'immense', 'massive', 'giant', 'colossal', 'monumental', 'tremendous', 'stupendous',
        'fantastic', 'fabulous', 'wonderful', 'marvelous', 'splendid', 'magnificent', 'glorious', 'brilliant', 'radiant', 'dazzling',
        'shining', 'gleaming', 'sparkling', 'twinkling', 'glittering', 'shimmering', 'glowing', 'luminous', 'bright', 'clear',
        'abc', 'ace', 'act', 'add', 'age', 'ago', 'aim', 'ale', 'all', 'amp',
        'and', 'ant', 'any', 'ape', 'app', 'apt', 'arc', 'are', 'ark', 'arm',
        'art', 'ash', 'ask', 'ate', 'avg', 'awe', 'axe', 'aye', 'bad', 'bag',
        'ban', 'bar', 'bat', 'bay', 'bed', 'bee', 'beg', 'bet', 'bid', 'bio',
        'bot', 'bow', 'box', 'boy', 'bro', 'bud', 'bug', 'bun', 'bus', 'but',
        'buy', 'cab', 'cam', 'can', 'cap', 'car', 'cat', 'cgi', 'chi', 'cli',
        'cog', 'com', 'con', 'cop', 'cos', 'cot', 'cow', 'coy', 'cry', 'cub',
        'cue', 'cup', 'cur', 'dad', 'dam', 'dat', 'day', 'def', 'den', 'dev',
        'dew', 'did', 'die', 'dig', 'dim', 'din', 'dip', 'doc', 'doe', 'dog',
        'dot', 'dry', 'dub', 'dud', 'due', 'dug', 'dye', 'ear', 'eat', 'ebb',
        'eco', 'edu', 'eel', 'egg', 'ego', 'elf', 'elm', 'emu', 'era', 'err',
        'eve', 'ewe', 'eye', 'fab', 'fad', 'fan', 'far', 'fat', 'fax', 'fed',
        'fee', 'fig', 'fin', 'fir', 'fit', 'fix', 'flu', 'fly', 'foe', 'fog',
        'for', 'fox', 'fry', 'fun', 'fur', 'gap', 'gas', 'gay', 'gel', 'gem',
        'gen', 'geo', 'gig', 'gin', 'gnu', 'god', 'got', 'gov', 'gps', 'grp',
        'gum', 'gun', 'gut', 'guy', 'gym', 'had', 'hag', 'ham', 'has', 'hat',
        'hay', 'hem', 'hen', 'her', 'hex', 'hey', 'hid', 'him', 'his', 'hob',
        'hog', 'hot', 'how', 'hub', 'hue', 'hug', 'hum', 'hut', 'ice', 'icy',
        'ids', 'ill', 'imp', 'inc', 'ink', 'inn', 'ion', 'irs', 'its', 'ivy',
        'jab', 'jag', 'jam', 'jar', 'jaw', 'jay', 'jet', 'job', 'jog', 'jot',
        'joy', 'jug', 'keg', 'ken', 'kin', 'kit', 'lab', 'lac', 'lad', 'lag',
        'lap', 'law', 'lax', 'lay', 'lea', 'led', 'leg', 'let', 'lib', 'lid',
        'lie', 'lip', 'lit', 'log', 'lot', 'low', 'lux', 'mac', 'mad', 'mag',
        'man', 'map', 'mat', 'may', 'men', 'met', 'mid', 'mix', 'mob', 'mod',
        'mom', 'mop', 'mud', 'mug', 'nag', 'nap', 'nav', 'nay', 'net', 'new',
        'nib', 'nil', 'nit', 'nod', 'nor', 'not', 'now', 'nub', 'nun', 'nut',
        'oak', 'oar', 'oat', 'odd', 'ode', 'ohm', 'oil', 'old', 'opt', 'orb',
        'ore', 'org', 'our', 'out', 'owe', 'owl', 'own', 'pac', 'pad', 'pal',
        'pan', 'par', 'pat', 'paw', 'pea', 'peg', 'pen', 'pep', 'per', 'pet',
        'pew', 'pic', 'pie', 'pig', 'pin', 'pit', 'ply', 'pod', 'pop', 'pot',
        'pow', 'pox', 'pre', 'pro', 'pry', 'pub', 'pug', 'pun', 'pup', 'put',
        'qua', 'rad', 'rag', 'ram', 'ran', 'rap', 'rat', 'raw', 'ray', 'rec',
        'ref', 'reg', 'rem', 'rep', 'ret', 'rev', 'rib', 'rid', 'rig', 'rim',
        'rip', 'rob', 'rod', 'roe', 'rot', 'row', 'rub', 'rug', 'rum', 'run',
        'rut', 'rye', 'sac', 'sad', 'sag', 'sap', 'sat', 'saw', 'sax', 'say',
        'sea', 'sec', 'see', 'set', 'sew', 'she', 'shy', 'sic', 'sim', 'sip',
        'sir', 'sis', 'sit', 'six', 'ska', 'ski', 'sly', 'sms', 'sob', 'sod',
        'son', 'sop', 'sot', 'sow', 'sox', 'soy', 'spa', 'spy', 'sql', 'std',
        'sub', 'sue', 'sum', 'sun', 'sup', 'sys', 'tab', 'tad', 'tag', 'tan',
        'tar', 'tax', 'tea', 'tee', 'ten', 'the', 'thy', 'tic', 'tie', 'tin',
        'tip', 'tis', 'toe', 'ton', 'too', 'toy', 'try', 'tub', 'tug', 'tux',
        'two', 'ugh', 'urn', 'use', 'van', 'vat', 'vet', 'vex', 'vhs', 'vie',
        'vim', 'vip', 'viz', 'vow', 'wad', 'wag', 'war', 'was', 'wax', 'web',
        'wed', 'wee', 'wet', 'who', 'why', 'wig', 'win', 'wit', 'woe', 'wok',
        'won', 'woo', 'wow', 'wtf', 'xml', 'yak', 'yam', 'yap', 'yaw', 'yea',
        'yes', 'yet', 'yew', 'yin', 'yup', 'zap', 'zen', 'zoo', 'zap', 'zed',
        'aba', 'abb', 'abd', 'abe', 'abi', 'abl', 'abn', 'abo', 'abs', 'abu',
        'aca', 'acc', 'acd', 'ach', 'ack', 'acm', 'acs', 'ada', 'adc', 'ade',
        'adm', 'ado', 'ads', 'adv', 'ady', 'aei', 'aer', 'aes', 'afa', 'afc',
        'aff', 'afk', 'afr', 'aft', 'aga', 'agb', 'agc', 'agd', 'agh', 'agi',
        'agl', 'agm', 'agn', 'ags', 'agt', 'agu', 'aha', 'ahd', 'ahi', 'ahl',
        'aho', 'ahs', 'aia', 'aib', 'aid', 'aif', 'aig', 'ail', 'ain', 'air',
        'ais', 'ait', 'aix', 'aja', 'ajc', 'aji', 'aka', 'akc', 'ake', 'aki',
        'ala', 'alb', 'alc', 'ald', 'alf', 'alg', 'ali', 'alk', 'alm', 'aln',
        'alo', 'alp', 'als', 'alt', 'alu', 'alv', 'alw', 'aly', 'ama', 'amb',
        'amc', 'amd', 'ame', 'ami', 'amk', 'aml', 'amm', 'amn', 'amo', 'ams',
        'amt', 'amu', 'amy', 'ana', 'anb', 'anc', 'ane', 'ang', 'ani', 'anj',
        'ank', 'anl', 'ann', 'ano', 'ans', 'anu', 'anx', 'aob', 'aod', 'aof',
        'aoi', 'aok', 'aol', 'aon', 'aos', 'aot', 'apa', 'apc', 'apd', 'api',
        'apl', 'apm', 'apn', 'apo', 'apr', 'aps', 'apu', 'aqb', 'aqc', 'aqe',
        'aqi', 'aql', 'aqm', 'aqn', 'aqp', 'aqr', 'aqs', 'aqu', 'ara', 'arb',
        'ard', 'arf', 'arg', 'ari', 'arl', 'arn', 'aro', 'arp', 'arr', 'ars',
        'aru', 'arv', 'arw', 'ary', 'asa', 'asb', 'asc', 'asd', 'ase', 'asf',
        'asg', 'asi', 'asl', 'asm', 'asn', 'aso', 'asp', 'asr', 'ass', 'ast',
        'asu', 'asw', 'asy', 'ata', 'atb', 'atc', 'atd', 'atf', 'atg', 'ath',
        'ati', 'atk', 'atl', 'atm', 'atn', 'ato', 'atp', 'atr', 'ats', 'att',
        'atu', 'atv', 'atw', 'aty', 'aua', 'aub', 'auc', 'aud', 'auf', 'aug',
        'auk', 'aul', 'aum', 'aun', 'aup', 'aur', 'aus', 'aut', 'auv', 'aux',
        'ava', 'avb', 'avc', 'avd', 'ave', 'avi', 'avl', 'avn', 'avo', 'avp',
        'avr', 'avs', 'avt', 'avu', 'avw', 'avy', 'awa', 'awb', 'awc', 'awd',
        'awf', 'awg', 'awk', 'awl', 'awm', 'awn', 'awo', 'awp', 'awr', 'aws',
        'awt', 'awu', 'awx', 'awy', 'axa', 'axb', 'axc', 'axd', 'axf', 'axg',
        'axi', 'axl', 'axm', 'axn', 'axo', 'axp', 'axr', 'axs', 'axt', 'axu',
        'axw', 'axy', 'aya', 'ayb', 'ayc', 'ayd', 'ayf', 'ayg', 'ayh', 'ayi',
        'ayl', 'aym', 'ayn', 'ayo', 'ayp', 'ayr', 'ays', 'ayt', 'ayu', 'ayv',
        'ayw', 'aza', 'azb', 'azc', 'azd', 'aze', 'azf', 'azg', 'azh', 'azi',
        'azl', 'azm', 'azn', 'azo', 'azp', 'azr', 'azs', 'azt', 'azu', 'azw',
        'azy', 'baa', 'bab', 'bac', 'bae', 'baf', 'bah', 'bai', 'baj', 'bak',
        'bal', 'bam', 'bao', 'bap', 'baq', 'bas', 'bau', 'bav', 'baw', 'bax',
        'baz', 'bba', 'bbb', 'bbc', 'bbd', 'bbe', 'bbf', 'bbg', 'bbi', 'bbj',
        'bbk', 'bbl', 'bbm', 'bbn', 'bbo', 'bbp', 'bbq', 'bbr', 'bbs', 'bbt',
        'bbu', 'bbv', 'bbw', 'bbx', 'bby', 'bbz', 'bca', 'bcb', 'bcc', 'bcd',
        'bce', 'bcf', 'bcg', 'bch', 'bci', 'bcj', 'bck', 'bcl', 'bcm', 'bcn',
        'bco', 'bcp', 'bcr', 'bcs', 'bct', 'bcu', 'bcv', 'bcw', 'bcx', 'bcy',
        'bcz', 'bda', 'bdb', 'bdc', 'bdd', 'bde', 'bdf', 'bdg', 'bdh', 'bdi',
        'bdj', 'bdk', 'bdl', 'bdm', 'bdn', 'bdo', 'bdp', 'bdr', 'bds', 'bdt',
        'bdu', 'bdv', 'bdw', 'bdx', 'bdy', 'bdz', 'bea', 'beb', 'bec', 'bef',
        'beh', 'bei', 'bej', 'bek', 'bel', 'bem', 'ben', 'beo', 'bep', 'beq',
        'ber', 'bes', 'beu', 'bev', 'bew', 'bex', 'bey', 'bez', 'bfa', 'bfb',
        'bfc', 'bfd', 'bfe', 'bff', 'bfg', 'bfh', 'bfi', 'bfj', 'bfk', 'bfl',
        'bfm', 'bfn', 'bfo', 'bfp', 'bfr', 'bfs', 'bft', 'bfu', 'bfv', 'bfw',
        'bfx', 'bfy', 'bfz', 'bga', 'bgb', 'bgc', 'bgd', 'bge', 'bgf', 'bgg',
        'bgh', 'bgi', 'bgj', 'bgk', 'bgl', 'bgm', 'bgn', 'bgo', 'bgp', 'bgr',
        'bgs', 'bgt', 'bgu', 'bgv', 'bgw', 'bgx', 'bgy', 'bgz', 'bha', 'bhb',
        'bhc', 'bhd', 'bhe', 'bhf', 'bhg', 'bhh', 'bhi', 'bhj', 'bhk', 'bhl',
        'bhm', 'bhn', 'bho', 'bhp', 'bhr', 'bhs', 'bht', 'bhu', 'bhv', 'bhw',
        'able', 'ajax', 'alfa', 'ally', 'apex', 'arch', 'area', 'atom', 'auto', 'axis',
        'baby', 'back', 'ball', 'band', 'bank', 'base', 'bass', 'bath', 'beam', 'bean',
        'bear', 'beat', 'been', 'beer', 'bell', 'belt', 'bend', 'beta', 'bike', 'bird',
        'bite', 'blow', 'blue', 'blur', 'boat', 'body', 'bond', 'bone', 'book', 'boom',
        'boot', 'boss', 'both', 'bowl', 'boys', 'buck', 'bulk', 'bull', 'burn', 'bush',
        'busy', 'byte', 'cafe', 'cage', 'cake', 'call', 'calm', 'came', 'camp', 'card',
        'care', 'cart', 'case', 'cash', 'cast', 'cave', 'cell', 'chat', 'chef', 'chip',
        'city', 'clay', 'clip', 'club', 'coal', 'coat', 'code', 'coin', 'coke', 'cold',
        'come', 'cook', 'copy', 'core', 'cork', 'corn', 'cost', 'cove', 'crew', 'crop',
        'cube', 'cure', 'curl', 'dame', 'damp', 'dare', 'data', 'date', 'dawn', 'days',
        'dead', 'deal', 'dean', 'dear', 'debt', 'deck', 'deep', 'deer', 'demo', 'deny',
        'desk', 'dice', 'diet', 'dime', 'disk', 'dive', 'dock', 'dome', 'done', 'doom',
        'door', 'dose', 'down', 'drag', 'draw', 'drew', 'drip', 'drop', 'drum', 'dual',
        'duck', 'dude', 'duke', 'dull', 'dumb', 'dump', 'dune', 'dunk', 'dusk', 'dust',
        'duty', 'each', 'earl', 'earn', 'ease', 'east', 'edge', 'edit', 'epic', 'euro',
        'even', 'ever', 'evil', 'exam', 'expo', 'face', 'fact', 'fade', 'fail', 'fair',
        'fake', 'fall', 'fame', 'farm', 'fate', 'fear', 'feat', 'feed', 'feel', 'feet',
        'fell', 'felt', 'file', 'fill', 'film', 'fine', 'firm', 'fish', 'fist', 'five',
        'flag', 'flap', 'flat', 'flaw', 'fled', 'flee', 'flew', 'flex', 'flip', 'flow',
        'flux', 'foam', 'folk', 'fond', 'font', 'food', 'fool', 'foot', 'fork', 'fort',
        'foul', 'four', 'fowl', 'frog', 'from', 'fuel', 'full', 'fume', 'fund', 'fuse',
        'fuze', 'gain', 'gala', 'gale', 'game', 'gang', 'gate', 'gave', 'gaze', 'gear',
        'gene', 'germ', 'gift', 'gild', 'gilt', 'girl', 'give', 'glad', 'glow', 'glue',
        'goal', 'goat', 'goes', 'gold', 'golf', 'gone', 'gong', 'gray', 'grew', 'grid',
        'grim', 'grin', 'grip', 'grow', 'gulf', 'gull', 'guru', 'gust', 'guys', 'hack',
        'hail', 'hair', 'half', 'hall', 'halt', 'hand', 'hang', 'hard', 'hare', 'harm',
        'harp', 'have', 'hawk', 'haze', 'hazy', 'head', 'heal', 'heap', 'heat', 'heed',
        'heel', 'held', 'hell', 'helm', 'help', 'hemp', 'herb', 'herd', 'hero', 'hide',
        'high', 'hike', 'hill', 'hilt', 'hint', 'hire', 'hive', 'hold', 'hole', 'holy',
        'home', 'hone', 'hood', 'hoof', 'hook', 'hoop', 'hope', 'horn', 'host', 'hour',
        'huge', 'hull', 'hung', 'hunt', 'hurt', 'hush', 'hymn', 'icon', 'idea', 'idle',
        'idly', 'inch', 'info', 'iris', 'iron', 'isle', 'item', 'jade', 'jail', 'jane',
        'jazz', 'jean', 'jeep', 'jerk', 'john', 'join', 'joke', 'jolt', 'josh', 'jury',
        'just', 'jute', 'keen', 'keep', 'kept', 'kick', 'kill', 'kilo', 'kind', 'king',
        'kiss', 'kite', 'knee', 'knew', 'knit', 'knob', 'knot', 'know', 'lace', 'lack',
        'lady', 'laid', 'lair', 'lake', 'lamb', 'lame', 'lamp', 'land', 'lava', 'lawn',
        'lazy', 'lead', 'leaf', 'leak', 'lean', 'leap', 'left', 'lend', 'lens', 'lent',
        'less', 'liar', 'lice', 'lick', 'life', 'lift', 'like', 'lily', 'limb', 'lime',
        'limp', 'line', 'lion', 'lite', 'load', 'loaf', 'loan', 'lobe', 'loch', 'loft',
        'logo', 'lone', 'loop', 'loot', 'lord', 'lore', 'lose', 'loss', 'lost', 'loud',
        'love', 'luck', 'lump', 'luna', 'lung', 'lure', 'lush', 'lust', 'lute', 'lynx',
        'mace', 'made', 'magi', 'maid', 'mail', 'main', 'make', 'male', 'mall', 'malt',
        'mama', 'mane', 'mare', 'mars', 'mash', 'mask', 'mast', 'mate', 'math', 'mayo',
        'maze', 'mead', 'meal', 'mean', 'meat', 'meek', 'meet', 'meld', 'melt', 'memo',
        'mend', 'menu', 'meow', 'mere', 'mesa', 'mesh', 'mess', 'mica', 'mice', 'mild',
        'mile', 'milk', 'mill', 'mime', 'mind', 'mine', 'mini', 'mink', 'mint', 'mire',
        'miss', 'mist', 'mite', 'mitt', 'moan', 'moat', 'mock', 'mode', 'mold', 'mole',
        'molt', 'monk', 'mood', 'moor', 'moot', 'mope', 'more', 'morn', 'moss', 'most',
        'moth', 'much', 'muck', 'mule', 'mull', 'murk', 'muse', 'mush', 'musk', 'must',
        'mute', 'mutt', 'myth', 'nail', 'name', 'navy', 'near', 'neat', 'neck', 'need',
        'neon', 'nest', 'news', 'newt', 'next', 'nice', 'nick', 'node', 'none', 'noon',
        'norm', 'nose', 'nous', 'nova', 'nude', 'null', 'numb', 'obey', 'omen', 'omit',
        'once', 'onto', 'opal', 'oral', 'orca', 'ounce', 'oval', 'oven', 'over', 'owed',
        'owes', 'pace', 'pack', 'pact', 'page', 'paid', 'pail', 'pain', 'pair', 'palm',
        'pane', 'pant', 'papa', 'park', 'part', 'past', 'pave', 'pawn', 'peak', 'peal',
        'pear', 'peat', 'peel', 'peer', 'pelt', 'perk', 'pest', 'pick', 'pier', 'pike',
        'pile', 'pill', 'pine', 'pink', 'pint', 'pipe', 'pity', 'plan', 'play', 'plea',
        'plot', 'plow', 'ploy', 'plug', 'plum', 'poet', 'poke', 'pole', 'poll', 'polo',
        'pond', 'pony', 'pool', 'poor', 'pope', 'pore', 'pork', 'port', 'pose', 'post',
        'pour', 'pray', 'prey', 'prim', 'prod', 'prof', 'prom', 'prop', 'pros', 'prow',
        'prune', 'puff', 'pull', 'pulp', 'puma', 'pump', 'punk', 'puny', 'pupa', 'pure',
        'purr', 'quad', 'quay', 'quit', 'quiz', 'race', 'rack', 'raft', 'rage', 'raid',
        'rail', 'rake', 'ramp', 'rang', 'rank', 'rant', 'rare', 'rash', 'rate', 'rave',
        'rays', 'raze', 'read', 'real', 'ream', 'reap', 'rear', 'reed', 'reef', 'reel',
        'rely', 'rend', 'rent', 'rest', 'rice', 'rich', 'ride', 'rife', 'rift', 'ring',
        'rink', 'riot', 'ripe', 'rise', 'risk', 'rite', 'road', 'roam', 'roar', 'robe',
        'rock', 'rode', 'role', 'roof', 'room', 'root', 'rope', 'rose', 'rosy', 'rote',
        'rout', 'rove', 'rows', 'rude', 'ruin', 'rule', 'rung', 'runt', 'ruse', 'rust',
        'ruth', 'sack', 'safe', 'saga', 'sage', 'said', 'sail', 'sake', 'sale', 'salt',
        'same', 'sand', 'sane', 'sang', 'sank', 'sash', 'save', 'says', 'scab', 'scan',
        'scar', 'seal', 'seam', 'sear', 'seas', 'seat', 'sect', 'seed', 'seek', 'seem',
        'seen', 'seep', 'self', 'sell', 'semi', 'send', 'sent', 'sept', 'serv', 'sets',
        'sewn', 'shed', 'shin', 'ship', 'shoe', 'shop', 'shot', 'show', 'shut', 'sick',
        'side', 'sift', 'sigh', 'silk', 'sill', 'silo', 'silt', 'sine', 'sing', 'site',
        'situ', 'size', 'skid', 'skim', 'skin', 'skip', 'skit', 'slab', 'slam', 'slap',
        'slat', 'slay', 'sled', 'slew', 'slid', 'slim', 'slit', 'slob', 'slop', 'slot',
        'slow', 'slug', 'slum', 'smog', 'snap', 'snip', 'snow', 'snub', 'snug', 'soak',
        'soap', 'soar', 'sock', 'soda', 'sofa', 'soil', 'sold', 'sole', 'solo', 'some',
        'song', 'soon', 'soot', 'sore', 'sort', 'soul', 'soup', 'sour', 'span', 'spar',
        'spec', 'sped', 'spin', 'spit', 'spot', 'spun', 'spur', 'stab', 'stag', 'star',
        'stat', 'stay', 'stem', 'step', 'stew', 'stir', 'stop', 'stow', 'stub', 'stud',
        'stun', 'such', 'suds', 'sued', 'suit', 'sulk', 'sung', 'sunk', 'sure', 'surf',
        'swab', 'swag', 'swam', 'swan', 'swap', 'swat', 'sway', 'swim', 'sync', 'tabs',
        'tack', 'taco', 'tact', 'tags', 'tail', 'take', 'tale', 'talk', 'tall', 'tame',
        'tang', 'tank', 'tape', 'taps', 'tare', 'tarn', 'tarp', 'tart', 'task', 'taxi',
        'teak', 'teal', 'team', 'tear', 'tech', 'teen', 'tell', 'temp', 'tend', 'tent',
        'term', 'tern', 'test', 'text', 'than', 'that', 'thaw', 'thee', 'them', 'then',
        'they', 'this', 'thud', 'thug', 'thus', 'tick', 'tide', 'tidy', 'tied', 'tier',
        'ties', 'tile', 'till', 'tilt', 'time', 'tint', 'tiny', 'tips', 'tire', 'toad',
        'toes', 'tofu', 'toga', 'told', 'toll', 'tomb', 'tome', 'tone', 'tong', 'tons',
        'took', 'tool', 'toot', 'tops', 'tore', 'torn', 'toss', 'tour', 'tout', 'town',
        'toys', 'tram', 'trap', 'tray', 'tree', 'trek', 'trim', 'trio', 'trip', 'trot',
        'troy', 'true', 'tsar', 'tube', 'tuck', 'tuft', 'tulip', 'tuna', 'tune', 'turf',
        'turn', 'tusk', 'tutu', 'twin', 'twig', 'type', 'undo', 'unit', 'unto', 'upon',
        'urge', 'used', 'user', 'uses', 'vain', 'vale', 'vane', 'vary', 'vase', 'vast',
        'vats', 'veal', 'veer', 'veil', 'vein', 'vend', 'vent', 'verb', 'very', 'vest',
        'veto', 'vial', 'vice', 'view', 'vile', 'vine', 'visa', 'vise', 'void', 'volt',
        'vote', 'wade', 'wage', 'wail', 'wait', 'wake', 'walk', 'wall', 'wand', 'wane',
        'want', 'ward', 'ware', 'warm', 'warn', 'warp', 'wars', 'wart', 'wary', 'wash',
        'wasp', 'wave', 'wavy', 'ways', 'weak', 'weal', 'wean', 'wear', 'webs', 'weed',
        'week', 'weep', 'weld', 'well', 'welt', 'went', 'wept', 'were', 'west', 'what',
        'when', 'whim', 'whip', 'whir', 'wick', 'wide', 'wife', 'wild', 'will', 'wilt',
        'wily', 'wind', 'wine', 'wing', 'wink', 'wipe', 'wire', 'wiry', 'wise', 'wish',
        'wisp', 'with', 'woke', 'wolf', 'womb', 'wood', 'wool', 'word', 'wore', 'work',
        'worm', 'worn', 'wrap', 'wren', 'yank', 'yard', 'yarn', 'yawn', 'year', 'yell',
        'yelp', 'yoga', 'yoke', 'yolk', 'your', 'yule', 'zeal', 'zero', 'zest', 'zinc',
        'zone', 'zoom',
        'about', 'above', 'abuse', 'acute', 'adapt', 'admit', 'adopt', 'adult', 'after', 'again',
        'agent', 'agree', 'ahead', 'alarm', 'album', 'alert', 'alien', 'align', 'alike', 'alive',
        'allow', 'alone', 'along', 'alpha', 'alter', 'amber', 'amend', 'among', 'angel', 'angle',
        'angry', 'apart', 'apple', 'apply', 'arena', 'argue', 'arise', 'armed', 'armor', 'array',
        'arrow', 'asset', 'atlas', 'audio', 'avoid', 'awake', 'award', 'aware', 'badly', 'baker',
        'bands', 'basic', 'basis', 'beach', 'began', 'begin', 'being', 'below', 'bench', 'billy',
        'birth', 'black', 'blade', 'blame', 'blank', 'blast', 'blaze', 'bleed', 'blend', 'bless',
        'blind', 'blink', 'block', 'blood', 'bloom', 'board', 'boost', 'booth', 'bound', 'brain',
        'brake', 'brand', 'brave', 'bread', 'break', 'breed', 'brick', 'bride', 'brief', 'bring',
        'brink', 'broad', 'broke', 'brook', 'brown', 'brush', 'build', 'built', 'burst', 'buyer',
        'cable', 'camel', 'canal', 'candy', 'cargo', 'carry', 'catch', 'cause', 'cease', 'chain',
        'chair', 'chaos', 'charm', 'chart', 'chase', 'cheap', 'cheat', 'check', 'cheer', 'chess',
        'chest', 'chief', 'child', 'chill', 'china', 'chose', 'chunk', 'claim', 'clash', 'class',
        'clean', 'clerk', 'click', 'cliff', 'climb', 'cling', 'clock', 'clone', 'close', 'cloth',
        'cloud', 'clown', 'coach', 'coast', 'could', 'count', 'coupe', 'court', 'cover', 'crack',
        'craft', 'crane', 'crash', 'crazy', 'cream', 'creek', 'creep', 'crest', 'crime', 'crisp',
        'cross', 'crowd', 'crown', 'crude', 'cruel', 'crush', 'cubic', 'curve', 'cycle', 'daily',
        'dairy', 'dance', 'dealt', 'death', 'debut', 'decay', 'decor', 'decoy', 'delay', 'delta',
        'demon', 'dense', 'depot', 'depth', 'derby', 'devil', 'diary', 'digit', 'dirty', 'disco',
        'ditch', 'diver', 'dodge', 'doing', 'dolly', 'donor', 'doubt', 'dough', 'dover', 'dozen',
        'draft', 'drain', 'drama', 'drank', 'drawn', 'dream', 'dress', 'dried', 'drift', 'drill',
        'drink', 'drive', 'droit', 'drone', 'droop', 'drown', 'dwarf', 'dwell', 'dying', 'eager',
        'eagle', 'early', 'earth', 'eight', 'eject', 'elbow', 'elder', 'elect', 'elite', 'empty',
        'enact', 'endow', 'enemy', 'enjoy', 'enter', 'entry', 'equal', 'equip', 'erect', 'error',
        'erupt', 'essay', 'ether', 'ethic', 'event', 'every', 'exact', 'exert', 'exile', 'exist',
        'expel', 'extra', 'fable', 'faced', 'facet', 'facts', 'faint', 'fairy', 'faith', 'false',
        'fancy', 'fatal', 'fatty', 'fault', 'fauna', 'favor', 'feast', 'fence', 'ferry', 'fetch',
        'fever', 'fiber', 'field', 'fiery', 'fifth', 'fifty', 'fight', 'filth', 'final', 'first',
        'fixed', 'flame', 'flank', 'flare', 'flesh', 'flick', 'fling', 'flint', 'float', 'flock',
        'flood', 'floor', 'flora', 'flour', 'flown', 'fluid', 'fluke', 'flung', 'flute', 'focal',
        'focus', 'folly', 'force', 'forge', 'forth', 'forty', 'forum', 'found', 'frame', 'frank',
        'fraud', 'freak', 'fresh', 'friar', 'fried', 'front', 'frost', 'fruit', 'fully', 'fungi',
        'funky', 'funny', 'fuzzy', 'gamma', 'gauge', 'gavel', 'gears', 'geese', 'genre', 'ghost',
        'giant', 'given', 'gland', 'glare', 'glass', 'glaze', 'gleam', 'glean', 'glide', 'glint',
        'globe', 'gloom', 'glory', 'gloss', 'glove', 'gnome', 'going', 'grace', 'grade', 'grain',
        'grand', 'grant', 'grape', 'graph', 'grasp', 'grass', 'grave', 'graze', 'greed', 'greek',
        'greet', 'grief', 'grill', 'grime', 'grind', 'groan', 'groom', 'gross', 'group', 'grove',
        'growl', 'grown', 'guard', 'guess', 'guest', 'guide', 'guild', 'guilt', 'guise', 'gusty',
        'habit', 'hairy', 'handy', 'happy', 'hardy', 'harsh', 'haste', 'hasty', 'hatch', 'haunt',
        'haven', 'havoc', 'heard', 'heart', 'heath', 'heavy', 'hedge', 'helix', 'hello', 'hence',
        'heron', 'hilly', 'hinge', 'hired', 'hobby', 'hoist', 'honey', 'honor', 'hoped', 'horde',
        'horse', 'hotel', 'hound', 'house', 'hover', 'human', 'humid', 'humor', 'hurry', 'hyena',
        'icily', 'ideal', 'idiom', 'idiot', 'image', 'imply', 'inbox', 'incur', 'index', 'infer',
        'inkle', 'inner', 'input', 'inter', 'intro', 'ionic', 'irony', 'issue', 'ivory', 'japan',
        'jelly', 'jewel', 'jiffy', 'joint', 'joker', 'jolly', 'joust', 'judge', 'juice', 'juicy',
        'jumbo', 'jumpy', 'kafka', 'karma', 'kebab', 'knack', 'knead', 'kneel', 'knelt', 'knife',
        'knock', 'known', 'kudos', 'label', 'labor', 'laden', 'ladle', 'lance', 'large', 'laser',
        'latch', 'later', 'latin', 'laugh', 'layer', 'leach', 'learn', 'lease', 'leash', 'least',
        'leave', 'ledge', 'leech', 'legal', 'lemon', 'level', 'lever', 'light', 'limit', 'linen',
        'lingo', 'liver', 'lived', 'lively', 'lives', 'lobby', 'local', 'locke', 'lodge', 'logic',
        'login', 'logos', 'lofty', 'loose', 'lorry', 'loser', 'lotus', 'lover', 'lower', 'loyal',
        'lucid', 'lucky', 'lumpy', 'lunar', 'lunch', 'lupus', 'lusty', 'luxe', 'lying', 'lyric',
        'macro', 'madam', 'magic', 'major', 'maker', 'mango', 'mania', 'manor', 'maple', 'march',
        'maria', 'marsh', 'mason', 'match', 'matte', 'mauve', 'maxim', 'maybe', 'mayor', 'meant',
        'media', 'medic', 'melee', 'melon', 'merge', 'merit', 'merry', 'metal', 'meter', 'metro',
        'micro', 'midst', 'might', 'minor', 'minus', 'misty', 'mitten', 'mixed', 'mixer', 'modal',
        'model', 'modem', 'moist', 'molar', 'money', 'month', 'moral', 'moron', 'morph', 'motel',
        'motor', 'motto', 'mould', 'mound', 'mount', 'mouse', 'mouth', 'moved', 'mover', 'moves',
        'movie', 'mower', 'muddy', 'mummy', 'mural', 'music', 'musky', 'musty', 'muted', 'naked',
        'named', 'nanny', 'nasal', 'nasty', 'natal', 'naval', 'navel', 'needy', 'nerve', 'never',
        'newer', 'newly', 'night', 'ninth', 'noble', 'nobly', 'nodal', 'noisy', 'nomad', 'north',
        'notch', 'noted', 'novel', 'nurse', 'nylon', 'nymph', 'occur', 'ocean', 'octal', 'octet',
        'oddly', 'odour', 'offer', 'often', 'olive', 'onion', 'onset', 'opens', 'opera', 'optic',
        'orbit', 'order', 'organ', 'other', 'otter', 'ought', 'ounce', 'outdo', 'outer', 'ovary',
        'owing', 'owner', 'oxide', 'ozone', 'pagan', 'paint', 'pansy', 'paper', 'parch', 'party',
        'pasta', 'paste', 'pasty', 'patch', 'patio', 'pause', 'peace', 'peach', 'pearl', 'pedal',
        'penny', 'perch', 'peril', 'perks', 'petty', 'phase', 'phone', 'photo', 'piano', 'piece',
        'pilot', 'pinch', 'pixel', 'pizza', 'place', 'plain', 'plane', 'plant', 'plate', 'plaza',
        'plead', 'pleas', 'pleat', 'plight', 'plumb', 'plume', 'plump', 'plunk', 'plush', 'poach',
        'point', 'poise', 'poker', 'polar', 'polka', 'pooch', 'poppy', 'porch', 'poser', 'posit',
        'posse', 'pouch', 'pound', 'power', 'prawn', 'press', 'price', 'pride', 'prima', 'prime',
        'print', 'prior', 'prism', 'privy', 'prize', 'probe', 'prone', 'proof', 'prose', 'proud',
        'prove', 'proxy', 'prude', 'prune', 'psalm', 'pubic', 'pulse', 'punch', 'pupil', 'puppy',
        'purge', 'pussy', 'putty', 'quack', 'quail', 'quake', 'qualm', 'quark', 'quart', 'quash',
    ];

    // Add .top extensions to all shortener names
    urlShortenerNames.forEach(name => {
        combinations.push(`${name}.top`);
    });

    return combinations;
}

// Main scraping function
async function scrapDomains() {
    let browser;
    const results = [];
    const combinations = generateDomainCombinations();

    log(`Total kombinasi domain yang akan dicek: ${combinations.length}`);
    log('Memulai proses checking...\n');

    try {
        browser = await puppeteer.launch({
            headless: false, // Set to true if you want to run headless
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        const page = await browser.newPage();
        // Increase timeouts to allow the page more time to finish client-side checks
        // and render the availability elements. Set to 60s for better accuracy.
        page.setDefaultTimeout(60000);
        page.setDefaultNavigationTimeout(60000);

        // Navigate to the initial domain checker page
        log('Membuka halaman arenhost.id...');
        await page.goto('https://arenhost.id/client/cart.php?a=add&domain=register&query=', {
            waitUntil: 'networkidle2'
        });

        log('Halaman berhasil dibuka. Memulai checking domain...\n');

        // Process each domain combination
        for (let index = 0; index < combinations.length; index++) {
            const domain = combinations[index];

            try {
                // Navigate to the URL with the domain (including extension) as query parameter
                // Use encodeURIComponent to ensure special characters are encoded
                const checkUrl = `https://arenhost.id/client/cart.php?a=add&domain=register&query=${encodeURIComponent(domain)}`;

                log(`Mengecek domain: ${domain}`);
                await page.goto(checkUrl, {
                    waitUntil: 'networkidle2'
                });

                // Short pause after navigation/click to allow any client-side
                // processes to start (e.g. JS that kicks off the availability check).
                // This helps in cases where the availability elements are rendered
                // shortly after navigation but need a tiny delay before their
                // computed style updates to `display: block`.
                await page.waitForTimeout(3000);

                // Wait longer for the result to appear and have display: block
                // Increased timeout to 60s to improve accuracy for slow client-side checks
                await page.waitForFunction(() => {
                    const unavailableElement = document.querySelector('p.domain-unavailable.domain-checker-unavailable');
                    const availableElement = document.querySelector('p.domain-available.domain-checker-available');

                    const unavailableDisplayed = unavailableElement && window.getComputedStyle(unavailableElement).display === 'block';
                    const availableDisplayed = availableElement && window.getComputedStyle(availableElement).display === 'block';

                    return unavailableDisplayed || availableDisplayed;
                }, { timeout: 60000 });

                // Check which element is displayed
                const availableElement = await page.$eval('p.domain-available.domain-checker-available', el =>
                    window.getComputedStyle(el).display === 'block'
                ).catch(() => false);

                const unavailableElement = await page.$eval('p.domain-unavailable.domain-checker-unavailable', el =>
                    window.getComputedStyle(el).display === 'block'
                ).catch(() => false);

                let status = 'error';
                if (availableElement) {
                    status = 'tersedia';
                } else if (unavailableElement) {
                    status = 'tidak tersedia';
                }

                // Record the result
                const result = `${domain} | ${status}`;
                results.push(result);

                // Log progress
                const progressPercentage = ((index + 1) / combinations.length * 100).toFixed(2);
                log(`[${index + 1}/${combinations.length}] (${progressPercentage}%) ${result}`);

                // Save results periodically (every 100 domains)
                if ((index + 1) % 100 === 0) {
                    fs.writeFileSync(
                        'hasil_scrap.txt',
                        results.join('\n'),
                        { encoding: 'utf-8' }
                    );
                    log('Hasil disimpan ke hasil_scrap.txt');
                }
            } catch (error) {
                console.error(`Error processing domain ${domain}:`, error.message);
                results.push(`${domain} | error`);
                log(`Error untuk domain ${domain}: ${error.message}`);
            }
        }

        // Save final results
        fs.writeFileSync(
            'hasil_scrap.txt',
            results.join('\n'),
            { encoding: 'utf-8' }
        );

        log('\n✓ Semua domain sudah dicek.');
        log(`✓ Total domain yang dicek: ${combinations.length}`);
        log('✓ Hasil disimpan ke: hasil_scrap.txt');

        // Display summary
        const available = results.filter(r => r.includes('tersedia') && !r.includes('tidak')).length;
        const unavailable = results.filter(r => r.includes('tidak tersedia')).length;
        const errors = results.filter(r => r.includes('error')).length;

        log('\n=== RINGKASAN ===');
        log(`Domain Tersedia: ${available}`);
        log(`Domain Tidak Tersedia: ${unavailable}`);
        log(`Error: ${errors}`);

    } catch (error) {
        log('Error dalam proses scraping: ' + error);
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// Run the script
scrapDomains().catch(error => {
    log('Fatal error: ' + error);
    process.exit(1);
});