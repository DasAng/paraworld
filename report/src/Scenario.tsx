import React from 'react';
import Accordion from '@mui/material/Accordion';
import Grid from '@mui/material/Grid';
import AccordionSummary from '@mui/material/AccordionSummary';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Table from '@mui/material/Table';
import { AccordionDetails, Chip, createTheme, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { makeStyles  } from '@mui/styles';
import { green, orange, red } from '@mui/material/colors';
import { CreateUUID } from './Utils';
import Step from './Step';
import SpeedIcon from '@mui/icons-material/Speed';

const theme = createTheme();

const useStyles = makeStyles(() => ({
    Scenario: {
        marginTop: "10px"
    },
    ScenarioSuccessTitle: {
        backgroundColor: green[600],
        color: "#ffffff"
    },
    ScenarioFailedTitle: {
        backgroundColor: red[700],
        color: "#ffffff"
    },
    ScenarioUndefinedTitle: {
        backgroundColor: orange[700],
        color: "#ffffff"
    },
    scenarioTags: {
        marginTop: "15px",
        marginBottom: "10px",
        margin: theme.spacing(0,1)
    },
    smallIcon: {
        position: "relative",
        top: theme.spacing(0.5),
    }
}));


export default function Scenario(props: {scenario: any}): JSX.Element {
    
    const {scenario} = props;
    const classes = useStyles();

    const getStatusClassName = (status: string) : string => {
        switch(status) {
            case "success":
                return classes.ScenarioSuccessTitle;
            case "failed":
                return classes.ScenarioFailedTitle;
            case "skipped":
                return classes.ScenarioUndefinedTitle;
        }
        return classes.ScenarioUndefinedTitle;
    }

    // const renderTags = scenario.detail.tags.map((x: any) => {
    //     return (
    //     <React.Fragment key={x.id}>
    //         <Chip className={classes.scenarioTags}
    //             label={x.name}
    //             color="primary"
    //         />
    //     </React.Fragment>
    //     );
    // });

    const renderDescription = (description: string) => {
        if (description) {
            return (
                <Typography variant="body2" color="textSecondary" component="p" style={{whiteSpace: 'pre-wrap', marginBottom: 20, marginTop: 10}}>
                        {description}
                </Typography>
            )
        }
    }

    // const renderSteps = scenario.detail.steps.map((x:any) => {
    //     return (
    //         <React.Fragment key={CreateUUID()}>
    //             <Step step={x}></Step>
    //         </React.Fragment>
    //     );
    // });

    const renderDetail = (scenario: any) => {
        return (
            <Grid container spacing={2}>
                    <Grid item>
                    <Table aria-label="detail table">
                        <TableHead>
                            <TableRow>
                                <TableCell><SpeedIcon className={classes.smallIcon}></SpeedIcon> Elapsed: {scenario.elapsed.toFixed(2)} (s)</TableCell>
                            </TableRow>
                        </TableHead>
                    </Table>
                    </Grid>
                </Grid>
        )
    }
    
    const summaryClassName = getStatusClassName(scenario.status)

    return (
        <Accordion className={classes.Scenario} elevation={6}>
            <AccordionSummary className={summaryClassName}
             expandIcon={<ExpandMoreIcon />}>
                 <Typography>Scenario: {scenario.detail.name}</Typography>
             </AccordionSummary>
             <AccordionDetails style={{display: 'block'}}>
                {renderDetail(scenario)}
                {scenario.detail.tags.map((x: any) => {
                    return (
                    <React.Fragment key={x.id}>
                        <Chip className={classes.scenarioTags}
                            label={x.name}
                            color="primary"
                        />
                    </React.Fragment>
                    );
                })}
                {renderDescription(scenario.detail.description)}
                {scenario.detail.steps.map((x:any) => {
                    return (
                        <React.Fragment key={CreateUUID()}>
                            <Step step={x}></Step>
                        </React.Fragment>
                    );
                })}
            </AccordionDetails>
        </Accordion>
    )
}