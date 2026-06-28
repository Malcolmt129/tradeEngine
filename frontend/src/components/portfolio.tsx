import { useEffect, useState } from 'react'


function Portfolio() {

  type Position = {
    security: string;
    quantity: number;
    marketValue: number;

  }

  const [position, setPosition] useState<Postion>(null);
}


    export default Portfolio
