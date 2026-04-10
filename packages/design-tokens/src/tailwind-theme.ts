import { colors } from "./colors";
import { elevation } from "./elevation";
import { motion } from "./motion";
import { radius } from "./radius";
import { spacing } from "./spacing";
import { fontFamily, fontSize } from "./typography";

export const scientificTailwindTheme = {
  colors,
  spacing,
  borderRadius: radius,
  boxShadow: elevation,
  fontFamily,
  fontSize,
  transitionDuration: motion.duration,
  transitionTimingFunction: motion.easing,
} as const;
