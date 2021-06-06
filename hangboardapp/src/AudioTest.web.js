import React from 'react';

import SFXone from './sounds/1.mp3';
import SFXtwo from './sounds/2.mp3';
import SFXthree from './sounds/3.mp3';
import SFXfour from './sounds/4.mp3';
import SFXfive from './sounds/5.mp3';
import SFXsix from './sounds/6.mp3';
import SFXseven from './sounds/7.mp3';
import SFXeight from './sounds/8.mp3';
import SFXnine from './sounds/9.mp3';
import SFXten from './sounds/10.mp3';
import SFXdone from './sounds/done.mp3';
import SFXfailed from './sounds/failed.mp3';
import SFXready from './sounds/ready.mp3';
import SFXstarthang from './sounds/starthang.mp3';
import SFXstophang from './sounds/stophang.mp3';

/*
const AudioTest1 = ({effect}): Node => {
    playAudio = () => {
        new Audio({effect}).play();
    }
};
*/

class AudioTest extends React.Component{ // TBD: Parameter passing

    playAudio = () => {
      new Audio(SFXstarthang).play();
    }
  
    render() {
      return (
          <div>
            <button onClick={this.playAudio}>{this.props.effect}</button>
          </div>
      );
    }
  };
  
export default AudioTest;