/* eslint-disable @typescript-eslint/no-explicit-any*/
import React from 'react';
import {useGlobalContext} from './GlobalContext';
import ReactDataGrid from '@inovua/reactdatagrid-community'
import { TypeColumn } from '@inovua/reactdatagrid-community/types/TypeColumn';
import '@inovua/reactdatagrid-community/index.css'
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import Scenario from './Scenario';
import { CreateUUID } from './Utils';
import { TypeOnSelectionChangeArg } from '@inovua/reactdatagrid-community/types/TypeDataGridProps';
import { TypeRowSelection } from '@inovua/reactdatagrid-community/types';
import CancelIcon from '@mui/icons-material/Cancel';
import WarningIcon from '@mui/icons-material/Warning';
import PrivacyTipIcon from '@mui/icons-material/PrivacyTip';
import { Tooltip, Typography } from '@mui/material';

const columns : TypeColumn[] = [
  { name: 'name', header: 'Feature', minWidth: 50, defaultWidth: 200},
  { name: 'description', header: 'Description', minWidth: 50, defaultWidth: 300,
  render: ({value}) => {
    return (
      <Typography variant="body2" color="textSecondary" component="p" style={{whiteSpace: 'pre-wrap'}}>
              {value}
      </Typography>
    )
  }},
  { name: 'status', header: 'Status', minWidth: 50, headerAlign: 'center',textAlign: 'center',
  render: ({value}) => {
    if (value === 'success') {
      return (
        <Tooltip title={"Success"}>
        <CheckCircleIcon color={'success'}></CheckCircleIcon>
        </Tooltip>
      )
    }
    else if (value === 'incomplete') {
      return (
        <Tooltip title={"Some scenarios are skipped"}>
      <PrivacyTipIcon color={'info'}></PrivacyTipIcon>
      </Tooltip>
      )
    }
    else if (value === 'skipped') {
      return (
        <Tooltip title={"No scenarios have been executed"}>
      <WarningIcon color={'warning'}></WarningIcon>
      </Tooltip>
      )
    } else {
      return (
        <Tooltip title={"Failed"}>
        <CancelIcon color={'error'}></CancelIcon>
        </Tooltip>
      )
    }
  }},
  { name: "scenarioSuccess", header: "successfull scenarios", minWidth: 100},
  { name: "scenarioFailed", header: "failed scenarios", minWidth: 100},
  { name: "scenarioSkipped", header: "skipped scenarios", minWidth: 100}
];

const gridStyle = { minHeight: 550 }

export default function Features(): JSX.Element { 

  const {gherkin} = useGlobalContext();
  const [scenarios, setSelectedScenarios] = React.useState([]);

  const rows = [];

  let id = 0;
  for(const feature of gherkin) {
    id++;
    const successScenarioCount = feature.scenarios.filter((x: { status: string; }) => x.status === 'success').length;
    const failedScenarioCount = feature.scenarios.filter((x: { status: string; }) => x.status === 'failed').length;
    const skippedScenarioCount = feature.scenarios.filter((x: { status: string; }) => x.status === 'skipped').length;
    rows.push({name: feature.name, status: feature.status, scenarioSuccess: successScenarioCount, scenarioFailed: failedScenarioCount, scenarioSkipped: skippedScenarioCount, description: feature.description})
  }

  const onSelectionChange = (config: TypeOnSelectionChangeArg) => {
    const feature = findSelectedFeature(config.selected);
    console.log("selected feature:", feature);
    if(feature) {
      setSelectedScenarios(feature.scenarios)
    } else {
      setSelectedScenarios([])
    }
  }

  const findSelectedFeature = (featureName: TypeRowSelection) => {
    const feature = gherkin.find((x: { name: string; }) => x.name === featureName);
    return feature;
  }

  return (
      <div>
        <div>
        <ReactDataGrid
            idProperty="name"
            columns={columns}
            pagination="local"
            editable={false}
            multiSelect={false}
            dataSource={rows}
            style={gridStyle}
            checkboxColumn={false}
            selected={true}
            onSelectionChange={onSelectionChange}
          />
        </div>
          {scenarios.map((sc: any) => {
          return (
              <React.Fragment key={CreateUUID()}>
                  <Scenario scenario={sc}></Scenario>
              </React.Fragment>
            
          )
        })}
      </div>
  )

}