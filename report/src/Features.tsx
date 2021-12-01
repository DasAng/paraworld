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

const columns : TypeColumn[] = [
  { name: 'name', header: 'Feature', minWidth: 50, defaultFlex: 2},
  { name: 'status', header: 'Status', minWidth: 50,
  render: ({value}) => {
    if (value === 'success') {
      return (
        <CheckCircleIcon color={'success'}></CheckCircleIcon>
      )
    } else {
      return (
        <CancelIcon color={'error'}></CancelIcon>
      )
    }
  }},
];

const gridStyle = { minHeight: 550 }

export default function Features(): JSX.Element { 

  const {gherkin} = useGlobalContext();
  const [scenarios, setSelectedScenarios] = React.useState([]);

  const rows = [];

  let id = 0;
  for(const feature of gherkin) {
    id++;
    rows.push({name: feature.name, status: feature.status})
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