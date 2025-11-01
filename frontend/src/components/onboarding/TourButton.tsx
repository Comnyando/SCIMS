/**
 * Tour button component for starting onboarding tours.
 * 
 * Placeholder component - will trigger tours when implemented.
 */

import { Button, Intent } from "@blueprintjs/core";

interface TourButtonProps {
  tourName: string;
  text?: string;
}

export default function TourButton({ tourName, text = "Take Tour" }: TourButtonProps) {
  const handleClick = () => {
    // TODO: Integrate with TourProvider to start tour
    console.log(`Tour requested: ${tourName}`);
  };

  return (
    <Button
      icon="help"
      text={text}
      intent={Intent.PRIMARY}
      onClick={handleClick}
    />
  );
}

