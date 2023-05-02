import { useState } from 'react';
import RangeSelector, {
  Margin, Scale, Label, SliderMarker, Behavior, Format,
} from 'devextreme-react/range-selector';

import './range.css'



export default function Range() {

  return (
    <div className="range-container">
      <div className="range-selector-wrapper">
        <RangeSelector
          id="range-selector"
        >
          <Margin top={20} />
          <Scale
            minorTickInterval={0.001}
            tickInterval={0.005}
            startValue={0.004563}
            endValue={0.04976}>
            <Label>
              <Format type="fixedPoint" precision={3} />
            </Label>
          </Scale>
          <SliderMarker customizeText={formatText}>
            <Format type="fixedPoint" precision={4} />
          </SliderMarker>
          <Behavior snapToTicks={false} />
        </RangeSelector>
      </div>
    </div>
  );
}

function formatText({ valueText }) {
  return `${valueText} mg/L`;
}
