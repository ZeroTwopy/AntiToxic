serverId = 1234 # works only in this server
ignoredRoleId = 1234 # role that can bypass automod = 600 # mute time in seconds
toxicityThreshold = 0.60 # toxic level at which automod is taking actions (0-1) 0.13, 0.1, 0.6
muteTime = 7200 # mute time in seconds 7200s = 2h
whitelistedWords = [ # whitelisted words regex
    r'(?i)\bword\b'
]
blacklistedWords = [ # blacklisted words regex
    r'(?i)\bword\b'
]
