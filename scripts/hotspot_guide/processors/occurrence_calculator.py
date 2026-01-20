"""Calculate occurrence rates for species at hotspots."""

import sys
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, field

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hotspot_guide.config import (
    MIN_CHECKLISTS_THRESHOLD,
    HIGH_CONFIDENCE_MIN,
    MEDIUM_CONFIDENCE_MIN,
    SEASONS,
    RATE_DECIMAL_PLACES,
)


@dataclass
class SpeciesAtHotspot:
    """Data for a species occurrence at a specific hotspot."""
    locality_id: str
    hotspot_name: str
    latitude: float
    longitude: float
    detection_count: int
    total_checklists: int
    occurrence_rate: float
    avg_count: float | None
    max_count: int | None
    seasonal_rates: Dict[str, float]
    monthly_rates: Dict[int, float]
    confidence_level: str


@dataclass
class SpeciesGuide:
    """Complete guide for a single species."""
    common_name: str
    scientific_name: str
    total_detections: int
    total_hotspots_detected: int
    hotspots: List[SpeciesAtHotspot] = field(default_factory=list)


def get_months_for_season(season: str) -> List[int]:
    """Get month numbers for a season."""
    return SEASONS.get(season, [])


def determine_confidence(checklist_count: int) -> str:
    """Assign confidence level based on sample size."""
    if checklist_count >= HIGH_CONFIDENCE_MIN:
        return 'high'
    elif checklist_count >= MEDIUM_CONFIDENCE_MIN:
        return 'medium'
    else:
        return 'low'


def calculate_occurrence_rates(
    hotspot_data: Dict[str, Dict[str, Any]],
    species_detections: Dict[str, Dict[str, Dict[str, Any]]],
    min_checklists: int = MIN_CHECKLISTS_THRESHOLD,
) -> Dict[str, SpeciesGuide]:
    """
    Calculate occurrence rates for each species at each hotspot.

    Occurrence Rate = (# checklists where species detected) / (# complete checklists)

    Args:
        hotspot_data: Dictionary of hotspot metadata from checklist_counter
        species_detections: Dictionary of species detections from species_detector
        min_checklists: Minimum checklists required for a hotspot to be included

    Returns:
        Dictionary mapping species name to SpeciesGuide
    """
    species_guides: Dict[str, SpeciesGuide] = {}

    for species_name, hotspot_detections in species_detections.items():
        hotspots_list: List[SpeciesAtHotspot] = []
        total_detections = 0
        scientific_name = None

        for loc_id, detection_data in hotspot_detections.items():
            # Skip if hotspot not in our hotspot data
            if loc_id not in hotspot_data:
                continue

            hotspot = hotspot_data[loc_id]

            # Skip hotspots below confidence threshold
            if hotspot['total_checklists'] < min_checklists:
                continue

            # Get scientific name from first detection
            if scientific_name is None:
                scientific_name = detection_data['scientific_name']

            detection_count = len(detection_data['checklist_ids'])
            total_detections += detection_count
            occurrence_rate = detection_count / hotspot['total_checklists']

            # Calculate seasonal rates
            seasonal_rates: Dict[str, float] = {}
            for season_name, months in SEASONS.items():
                seasonal_checklists = sum(
                    hotspot['monthly_checklists'].get(m, 0) for m in months
                )
                if seasonal_checklists >= 5:  # Lower threshold for seasonal
                    seasonal_detections = sum(
                        len(detection_data['monthly_checklist_ids'].get(m, set()))
                        for m in months
                    )
                    rate = seasonal_detections / seasonal_checklists
                    seasonal_rates[season_name] = round(rate, RATE_DECIMAL_PLACES)

            # Calculate monthly rates
            monthly_rates: Dict[int, float] = {}
            for month in range(1, 13):
                month_checklists = hotspot['monthly_checklists'].get(month, 0)
                if month_checklists >= 3:  # Lower threshold for monthly
                    month_detections = len(
                        detection_data['monthly_checklist_ids'].get(month, set())
                    )
                    rate = month_detections / month_checklists
                    monthly_rates[month] = round(rate, RATE_DECIMAL_PLACES)

            # Calculate average count when present
            avg_count = None
            if detection_count > 0 and detection_data['total_count'] > 0:
                avg_count = round(detection_data['total_count'] / detection_count, 1)

            max_count = detection_data['max_count'] if detection_data['max_count'] > 0 else None

            confidence = determine_confidence(hotspot['total_checklists'])

            hotspots_list.append(SpeciesAtHotspot(
                locality_id=loc_id,
                hotspot_name=hotspot['name'],
                latitude=hotspot['latitude'],
                longitude=hotspot['longitude'],
                detection_count=detection_count,
                total_checklists=hotspot['total_checklists'],
                occurrence_rate=round(occurrence_rate, RATE_DECIMAL_PLACES),
                avg_count=avg_count,
                max_count=max_count,
                seasonal_rates=seasonal_rates,
                monthly_rates=monthly_rates,
                confidence_level=confidence,
            ))

        # Sort by occurrence rate (descending), then by detection count
        hotspots_list.sort(
            key=lambda x: (x.occurrence_rate, x.detection_count),
            reverse=True
        )

        species_guides[species_name] = SpeciesGuide(
            common_name=species_name,
            scientific_name=scientific_name or '',
            total_detections=total_detections,
            total_hotspots_detected=len(hotspots_list),
            hotspots=hotspots_list,
        )

    return species_guides
