const https = require('https');

exports.handler = async (event) => {
    const finding = event.detail.findings[0];

    const severity = finding.Severity.Label;
    const title = finding.Title;
    const description = finding.Description;
    const region = finding.Region;
    const account = finding.AwsAccountId;

    const link = `https://${region}.console.aws.amazon.com/securityhub/home?region=${region}#/findings?search=id%3D${encodeURIComponent(finding.Id)}`;

    const slackMessage = {
        blocks: [
            {
                type: "header",
                text: {
                    type: "plain_text",
                    text: `Security Hub Alert: ${severity} Severity`
                }
            },
            {
                type: "section",
                fields: [
                    { type: "mrkdwn", text: `*Account:* ${account}` },
                    { type: "mrkdwn", text: `*Region:* ${region}` }
                ]
            },
            {
                type: "section",
                text: {
                    type: "mrkdwn",
                    text: `*Title:* ${title}\n*Description:* ${description}`
                }
            },
            {
                type: "actions",
                elements: [
                    {
                        type: "button",
                        text: {
                            type: "plain_text",
                            text: "View Finding"
                        },
                        url: link
                    }
                ]
            }
        ]
    };

    const url = new URL(process.env.SLACK_WEBHOOK_URL);

    const options = {
        hostname: url.hostname,
        path: url.pathname,
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    };

    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            res.on('data', () => resolve('Message sent to Slack'));
        });

        req.on('error', (e) => reject(e));
        req.write(JSON.stringify(slackMessage));
        req.end();
    });
};
