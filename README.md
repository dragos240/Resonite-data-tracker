# VR-stat-tracker

## Usage

### Getting data from YUR

You'll need to get your YUR token and put it in a file named '.env' in the project root like this:
```
yur_token="TOKEN"
```

If the data is invalid, ensure the token is in the correct format. You want the token without `Bearer`.

**TODO**: Explain how to get said token

To gather data from `FROM_DATE` to `TO_DATE` run the following:
`python3 -m digger.grabber FROM_DATE TO_DATE`


### Plotting gathered data

To plot the collected data, run the following:
`python3 -m digger.plotting`

This will produce a `plots` directory with graphs for each kind of stat, currently:
- Average time per day by month
- Peak play times
- Time by week day
- Time by week number
- Time per day
