/* eslint-disable @typescript-eslint/no-explicit-any*/
import React from 'react';
import { makeStyles  } from '@mui/styles';
import { Box, Collapse, Tooltip, Typography } from '@mui/material';
import TimerIcon from '@mui/icons-material/Timer';
import TerminalTwoToneIcon from '@mui/icons-material/TerminalTwoTone';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HelpIcon from '@mui/icons-material/Help';
import { blue, green, orange, red } from '@mui/material/colors';
import CancelIcon from '@mui/icons-material/Cancel';
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';

const useStyles = makeStyles(() => ({
    statusIcon: {
        marginRight: 5
    },
    message: {
        whiteSpace: 'pre-wrap'
    },
    logContainer: {
        width: 20,
        marginRight: 5
    },
    attachment: {
        marginLeft: 20
    },
    logIcon: {
        cursor: "pointer",
    },
    argument: {
        whiteSpace: 'pre-wrap',
        marginLeft: 40,
        fontStyle: 'italic'
    },
    durationIcon: {
        marginLeft: 'auto',
        order: 2
    },
    stepError: {
        color: red[500],
        backgroundColor: "#f1f1f1"
    }
}));

export default function Step(props: {step: any}): JSX.Element {

    const {step} = props;

    console.log("render step:", step);

    const classes = useStyles();

    const [expanded, setExpanded] = React.useState(false);

    const handleShowLogs = () => {
        setExpanded(!expanded);
    };

    const renderStatusIcon = (status: string) : JSX.Element => {
        switch(status) {
            case 'skipped':
                return <Tooltip title="skipped"><PriorityHighIcon className={classes.statusIcon} fontSize="small" style={{color: orange[500]}}></PriorityHighIcon></Tooltip>
            case 'success':
                return <Tooltip title="passed"><CheckCircleIcon className={classes.statusIcon} fontSize="small" style={{color: green[500]}}></CheckCircleIcon></Tooltip>
            case 'failed':
                return <Tooltip title="failed"><CancelIcon className={classes.statusIcon} fontSize="small" style={{color: red[500]}}></CancelIcon></Tooltip>
        }
        return <Tooltip title="undefined"><HelpIcon className={classes.statusIcon} fontSize="small" style={{color: blue[500]}}></HelpIcon></Tooltip>
    }

    const showLogIcon = () => {
        return <div className={classes.logContainer}><Tooltip title="click to show or hide logs"><TerminalTwoToneIcon className={classes.logIcon} onClick={handleShowLogs}></TerminalTwoToneIcon></Tooltip></div>
    }

    // const renderArguments = () => {
    //     if (step.argument && step.argument.docString) {
    //         return <Typography className={classes.argument} variant="body2" color="textSecondary" component="p">{step.argument.docString.content}</Typography>
    //     }
    // }

    const renderDuration = (duration: number) => {
        const durationString = Number(duration).toFixed(3);
        if (duration > 5.0) {
            return (
            <Tooltip title="duration in seconds">
                    <Typography variant="body1" color="textPrimary" className={classes.durationIcon}>
                        <b>{durationString} (s)</b>
                    <TimerIcon></TimerIcon>
                    </Typography>
            </Tooltip>
            );
        }
        return (
            <Tooltip title="duration in seconds">
                <Typography variant="body1" color="textSecondary" className={classes.durationIcon}>
                    {durationString} (s)
                <TimerIcon></TimerIcon>
                </Typography>
            </Tooltip>
        )
    }

    const renderLog = (log: string) => {
        if (log) {
            return (
                <textarea
                    aria-label="log message"
                    defaultValue={log}
                    style={{ width: '100%', height: 390, overflow: "auto",display: 'flex', resize: 'none' }}
                    readOnly
                    />
            )
        }
    }

    const renderError = (error: string) => {
        if (error) {
            return (
                <pre style={{whiteSpace: "pre-wrap"}}>
                    <code className={classes.stepError}>
                        {error}
                    </code>
                </pre>
            )
        }
    }
    
    return (
        <div>
            <Box display="flex" >
                {showLogIcon()}
                {renderStatusIcon(step.status)}
                <Typography><b>{step.keyword}</b> {step.text}</Typography>
                {renderDuration(step.elapsed)}
            </Box>
            {/* {renderArguments()} */}
            {/* <code className={classes.message}>{step.result.message}</code> */}
            <Collapse className={classes.attachment} in={expanded}>
                {renderError(step.error)}
                {renderLog(step.log)}
                {/* <Attachments attachments={step.attachments}></Attachments> */}
            </Collapse>
        </div>
    );
}