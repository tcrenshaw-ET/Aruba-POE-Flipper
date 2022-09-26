- depends on fabric.  
- assumes you have an ssh key for in .ssh that is for user "scripts" 
  - can define key location with `-k \where\da\key\at`
## current device type (-t) options
- uses a preset mac address prefix
- eztv `00:02:02`
- crestron `00:10:7f`
- dante `00:1d:c1`

## Example usage
- will flip POE to all the EZTV endpoints on switch at IP 172.25.1.32
`python3 ./poe_flipper.py -t eztv -s 172.25.1.32`
- does a "dry run" on dante endpoints across all of BDS `python3 ./poe_flipper.py -d -t dante -v BDS`
- use a custom mac address prefix `python3 `./poe_flipper.py -m de:ad:be:ef -s 192.168.1.2
