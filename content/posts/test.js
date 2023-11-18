const fs = require('fs');
const regex = /(\d+)-(\d+)-(\d+)-([^.]+)\.md/;
fs.readdir('.', function (err, files) {
    if (err) {
        console.error(err);
        return;
    }
    for (let file of files) {
        const match = regex.exec(file);
        if (match != null) {
            const slug = match[4].toLowerCase();
            let contents = fs.readFileSync(file, 'utf8').split('\n');
            let hasSlug = false;
            let hasDate = false;
            for (const line of contents) {
                if (line.indexOf('slug:') >= 0) {
                    hasSlug = true;
                }
                if (line.indexOf('date:') >= 0) {
                    hasDate = true;
                }
            }
            if (!hasSlug) {
                contents[0] = `${contents[0]}\nslug: ${slug}`;
                console.log('no slug', file);
            }
            if (!hasDate) {
                contents[0] = `${contents[0]}\ndate: ${match[1]}-${match[2]}-${match[3]}`;
                console.log('no date', file);
            }
            // console.log(file, contents[0]);
            // console.log("========")
            fs.writeFileSync(file, contents.join('\n'));
        }
    }
    // const matches = files.filter(file => regex.test(file));
    // console.log(matches);
});