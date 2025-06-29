
from datetime import datetime, timedelta
from django.conf import settings
from django.utils.timezone import now
from tools.models import SchoolProfileScan


DEFAULT_WEIGHTS = getattr(settings, "SCHOOL_PROFILE_ANALYSIS_WEIGHTS", {
    "profile_completeness": 0.25,
    "data_quality": 0.20,
    "visual_content": 0.20,
    "facilities": 0.15,
    "academic_info": 0.20,
})


# Fees analysis helper
def get_fees_analysis(data):
    fees_structure = data.get("fees_structure", {})
    selected_session = data.get("internal", {}).get("selected_session")
    class_list = [c.get("name") for c in data.get("classes", []) if c.get("name")]

    selected_session_fees = fees_structure.get(selected_session, [])

    # Filter out classes that have actual fee values
    classes_with_fees = set()
    for item in selected_session_fees:
        monthly_fee = item.get("monthly_fee")
        annual_fee = item.get("cost_of_year_for_new_admission")

        if (monthly_fee and monthly_fee != 0) or (annual_fee and annual_fee != 0):
            classes_with_fees.add(item.get("class"))

    missing_classes = [cls for cls in class_list if cls not in classes_with_fees]
    all_classes_have_fees = len(missing_classes) == 0

    # Determine if any valid fees are available for selected session
    latest_session_fees_available = len(classes_with_fees) > 0

    # Score calculation
    score = 0
    if latest_session_fees_available:
        score += 50
        score += round(((len(class_list) - len(missing_classes)) / len(class_list)) * 50, 1)

    return {
        "latest_session_fees_available": latest_session_fees_available,
        "missing_classes_in_selected_session": missing_classes,
        "fee_completeness_score": score
    }


def analyse_school_profile(data):
    """
    Super powerful school profile analyzer that evaluates all aspects of school data
    and provides comprehensive analysis with strength points and improvement suggestions.
    """
    
    analysis = {
        "overall_score": 0,
        "detailed_analysis": {},
        "strength_points": [],
        "improvement_suggestions": [],
        "recommendations": [],
        "data_insights": {}
    }
    
    # Initialize counters and flags
    total_fields = 0
    filled_fields = 0
    
    # 1. BASIC PROFILE INFORMATION ANALYSIS
    basic_info = {
        "name": data.get("name"),
        "slug": data.get("slug"), 
        "logo": data.get("logo"),
        "email": data.get("email"),
        "phone_no": data.get("phone_no"),
        "website": data.get("website"),
        "short_name": data.get("short_name")
    }
    
    basic_filled = sum(1 for v in basic_info.values() if v and str(v).strip())
    basic_score = (basic_filled / len(basic_info)) * 100
    
    # 2. ACADEMIC INFORMATION ANALYSIS
    academic_info = {
        "boards": data.get("boards", []),
        "classes_offered": data.get("classes_offered"),
        "medium": data.get("medium"),
        "languages_taught": data.get("languages_taught", []),
        "academic_session": data.get("academic_session"),
        "student_teacher_ratio": data.get("student_teacher_ratio")
    }
    
    academic_filled = 0
    if academic_info["boards"]: academic_filled += 1
    if academic_info["classes_offered"]: academic_filled += 1
    if academic_info["medium"]: academic_filled += 1
    if academic_info["languages_taught"]: academic_filled += 1
    if academic_info["academic_session"]: academic_filled += 1
    if academic_info["student_teacher_ratio"]: academic_filled += 1
    
    academic_score = (academic_filled / 6) * 100
    
    # 3. INFRASTRUCTURE AND FACILITIES ANALYSIS
    infrastructure = data.get("infrastruture", [])
    feature_facilities = data.get("feature_facilities", [])
    
    infra_score = 0
    total_infra_images = 0
    
    for infra in infrastructure:
        if infra.get("images"):
            total_infra_images += len(infra["images"])
            
    infra_categories = len(infrastructure)
    facility_features = sum(len(cat.get("features", [])) for cat in feature_facilities)
    
    if infra_categories > 0:
        infra_score = min(100, (infra_categories * 15) + min(50, total_infra_images * 2))
    
    # 4. VISUAL CONTENT ANALYSIS
    gallery = data.get("gallery", {})
    images = gallery.get("images", [])
    videos = gallery.get("videos", [])
    display_images = gallery.get("display_images", [])
    
    visual_score = 0
    if images:
        visual_score += min(40, len(images) * 2)  # Max 40 points for images
    if videos:
        visual_score += min(30, len(videos) * 6)  # Max 30 points for videos
    if display_images:
        visual_score += min(20, len(display_images) * 3)  # Max 20 points for display images
    if gallery.get("virtual_tour"):
        visual_score += 10  # Bonus for virtual tour
        
    visual_score = min(100, visual_score)
    
    # 5. FEES AND ADMISSION ANALYSIS
    fees_structure = data.get("fees_structure", {})
    admissions = data.get("admissions", {})
    
    fees_score = 0
    if fees_structure:
        available_sessions = len(fees_structure.keys())
        fees_score = min(100, available_sessions * 25)  # 25 points per session
        
    admission_score = 0
    if admissions.get("documents"):
        admission_score += 30
    if admissions.get("school_timings"):
        admission_score += 20
    if admissions.get("openSession"):
        admission_score += 30
    if data.get("pre_post_admission_process"):
        admission_score += 20
        
    # 6. CONTENT QUALITY ANALYSIS
    def normalized_text_score(text, max_score, max_len):
        if not text:
            return 0
        length = len(str(text).strip())
        if length >= max_len:
            return max_score
        return round((length / max_len) * max_score, 2)

    content_fields = {
        "about": (data.get("about"), 10, 1000),
        "usp": (data.get("usp"), 10, 600),
        "awards": (data.get("awards"), 10, 600),
        "pre_post_admission_process": (data.get("pre_post_admission_process"), 4, 200),
        "withdrawl_policy": (data.get("withdrawl_policy"), 4, 100),
        "scholarship": (data.get("scholarship"), 2, 100),
        "life_at_school": (data.get("life_at_school"), 4, 100),
        "infra_and_facilities": (data.get("infra_and_facilities"), 4, 100),
        "leader_messages": (data.get("leader_messages"), 1, 1),
        "events": (data.get("events"), 1, 1),
        "news": (data.get("news"), 1, 1),
    }

    content_score = 0
    total_possible_score = 0

    for field, (value, weight, max_len) in content_fields.items():
        if isinstance(value, list):
            value_score = weight if len(value) > 0 else 0
        else:
            value_score = normalized_text_score(value, weight, max_len)
        content_score += value_score
        total_possible_score += weight

    content_score = round((content_score / total_possible_score) * 100, 1)
                
    # 7. ADDRESS AND CONTACT ANALYSIS
    address = data.get("address", {})
    contact_score = 0
    
    address_fields = ["adress_1", "area", "district", "state", "pincode", "latitude", "longitude"]
    filled_address = sum(1 for field in address_fields if address.get(field))
    contact_score = (filled_address / len(address_fields)) * 100
    
    # 8. SPECIAL FEATURES ANALYSIS
    special_features = {
        "verified_by_school": data.get("verified_by_school", False),
        "year_of_establishment": data.get("year_of_establishment"),
        "built_in_area": data.get("built_in_area"),
        "number_of_students": data.get("number_of_students"),
        "brochure": data.get("brochure")
    }
    
    filled = sum(1 for v in special_features.values() if v)
    special_score = (filled / len(special_features)) * 100  # Cap at 100    
    
    # CALCULATE OVERALL SCORES
    profile_completeness_score = round((basic_score + academic_score + contact_score) / 3, 1)
    data_quality_score = round((content_score + special_score) / 2, 1)
    visual_content_score = round(visual_score, 1)
    infrastructure_score = round(infra_score, 1)
    contact_accessibility_score = round(contact_score, 1)
    academic_information_score = round(academic_score, 1)
    
    # Normalize scores to a maximum of 100 before applying weights
    def normalize(score):
        return min(score, 100)

    analysis["overall_score"] = round((
        normalize(profile_completeness_score) * 0.20 +
        normalize(data_quality_score) * 0.20 +
        normalize(visual_content_score) * 0.15 +
        normalize(infrastructure_score) * 0.15 +
        normalize(academic_information_score) * 0.20 +
        normalize(analysis["detailed_analysis"].get("data_completeness", {}).get("fee_completeness_score", 0)) * 0.10
    ), 1)
    
    # DETAILED INSIGHTS
    analysis["data_insights"] = {
        "total_images": len(images),
        "total_videos": len(videos),
        "infrastructure_categories": infra_categories,
        "total_infrastructure_images": total_infra_images,
        "facility_features_count": facility_features,
        "available_fee_sessions": len(fees_structure.keys()) if fees_structure else 0,
        "boards_offered": len(data.get("boards", [])),
        "classes_range": data.get("classes_offered", "Not specified"),
        "campus_size": data.get("built_in_area", "Not specified"),
        "student_count": data.get("number_of_students", "Not specified"),
        "establishment_year": data.get("year_of_establishment", "Not specified"),
        "view_count": data.get("views", 0)
    }
    
    # GENERATE STRENGTH POINTS
    strength_points = []
    
    if len(images) >= 15:
        strength_points.append(f"Excellent visual representation with {len(images)} high-quality gallery images")
    
    if len(videos) >= 3:
        strength_points.append(f"Strong multimedia content with {len(videos)} promotional videos")
        
    if infra_categories >= 6:
        strength_points.append(f"Comprehensive infrastructure documentation across {infra_categories} categories")
        
    if total_infra_images >= 20:
        strength_points.append(f"Detailed infrastructure showcase with {total_infra_images} facility images")
        
    if len(data.get("boards", [])) >= 2:
        strength_points.append(f"Multiple board options available: {', '.join(data.get('boards', []))}")
        
    if data.get("verified_by_school"):
        strength_points.append("School-verified profile ensuring authentic information")
        
    if data.get("year_of_establishment") and int(data.get("year_of_establishment", 0)) < 2010:
        strength_points.append(f"Well-established institution since {data.get('year_of_establishment')}")
        
    if data.get("built_in_area") and any(unit in str(data.get("built_in_area")).lower() for unit in ["acre", "sq ft"]):
        strength_points.append(f"Spacious campus with {data.get('built_in_area')} of built area")
        
    if len(fees_structure.keys()) >= 3:
        strength_points.append(f"Transparent fee structure available for {len(fees_structure.keys())} academic sessions")
        
    if data.get("awards") and len(str(data.get("awards"))) > 100:
        strength_points.append("Strong recognition with documented awards and achievements")
        
    if facility_features >= 15:
        strength_points.append(f"Well-equipped with {facility_features} documented facilities and features")
        
    if data.get("student_teacher_ratio"):
        ratio_parts = str(data.get("student_teacher_ratio")).split(":")
        if len(ratio_parts) == 2 and int(ratio_parts[0]) <= 15:
            strength_points.append(f"Excellent student-teacher ratio of {data.get('student_teacher_ratio')}")
    
    # GENERATE IMPROVEMENT SUGGESTIONS
    improvement_suggestions = []
    
    if len(images) < 10:
        improvement_suggestions.append("Add more high-quality photos of campus facilities and student activities")
        
    if len(videos) < 2:
        improvement_suggestions.append("Include school videos and virtual campus tours to enhance engagement")
        
    if not data.get("about") or len(str(data.get("about"))) < 200:
        improvement_suggestions.append("Expand the 'About Us' section with detailed school philosophy and vision")
        
    if not data.get("usp") or len(str(data.get("usp"))) < 100:
        improvement_suggestions.append("Add comprehensive Unique Selling Points (USP) to highlight school advantages")
        
    if infra_categories < 5:
        improvement_suggestions.append("Document more infrastructure categories with detailed descriptions")
        
    if total_infra_images < 15:
        improvement_suggestions.append("Include more infrastructure images to showcase facilities better")
        
    if not data.get("awards") or len(str(data.get("awards"))) < 50:
        improvement_suggestions.append("Add school awards, recognitions, and achievements section")
        
    if len(fees_structure.keys()) < 2:
        improvement_suggestions.append("Provide fee structure for multiple academic sessions")
        
    if not data.get("brochure"):
        improvement_suggestions.append("Upload school brochure for comprehensive information access")
        
    if not data.get("website") or not data.get("email"):
        improvement_suggestions.append("Update contact information including website and email details")
        
    if not address.get("latitude") or not address.get("longitude"):
        improvement_suggestions.append("Add precise location coordinates for better accessibility")
        
    if not data.get("pre_post_admission_process"):
        improvement_suggestions.append("Include detailed admission process and requirements")
        
    if facility_features < 10:
        improvement_suggestions.append("Document more facilities and features to showcase school amenities")
        
    if not gallery.get("virtual_tour"):
        improvement_suggestions.append("Add virtual tour link for immersive campus experience")
        
    if data.get("views", 0) < 5000:
        improvement_suggestions.append("Optimize profile content and SEO to increase visibility and views")
    
    # GENERATE RECOMMENDATIONS
    recommendations = []
    
    if analysis["overall_score"] >= 80:
        recommendations.append("Excellent profile! Focus on regular content updates and engagement")
    elif analysis["overall_score"] >= 60:
        recommendations.append("Good profile foundation. Enhance visual content and facility documentation")
    else:
        recommendations.append("Profile needs significant improvement in content quality and completeness")
        
    if visual_score < 50:
        recommendations.append("Prioritize adding high-quality images and videos for better engagement")
        
    if academic_score < 70:
        recommendations.append("Complete academic information including all curriculum details")
        
    if infra_score < 60:
        recommendations.append("Enhance infrastructure documentation with detailed descriptions and images")
    
    # Assign calculated values
    analysis["strength_points"] = strength_points[:8]  # Limit to top 8 points
    analysis["improvement_suggestions"] = improvement_suggestions[:10]  # Limit to top 10 suggestions
    analysis["recommendations"] = recommendations

    fees_analysis = get_fees_analysis(data)
    
    # DETAILED ANALYSIS BREAKDOWN
    analysis["detailed_analysis"] = {
        "profile_summary": {
            "school_name": data.get("name", "Not specified"),
            "location": f"{address.get('area', '')}, {address.get('district', '')}".strip(', '),
            "establishment_year": data.get("year_of_establishment", "Not specified"),
            "school_type": data.get("format", "Not specified"),
            "boards": data.get("boards", []),
            "classes": data.get("classes_offered", "Not specified"),
        },
        "content_analysis": {
            "visual_assets": {
                "gallery_images": len(images),
                "promotional_videos": len(videos),
                "infrastructure_images": total_infra_images,
            },
            "textual_content": {
                "about_length": len(str(data.get("about", ""))) if data.get("about") else 0,
                "usp_length": len(str(data.get("usp", ""))) if data.get("usp") else 0,
                "awards_length": len(str(data.get("awards", ""))) if data.get("awards") else 0,
                "pre_post_admission_process_length": len(str(data.get("pre_post_admission_process", ""))) if data.get("pre_post_admission_process") else 0,
                "withdrawl_policy_length": len(str(data.get("withdrawl_policy", ""))) if data.get("withdrawl_policy") else 0,
                "scholarship_length": len(str(data.get("scholarship", ""))) if data.get("scholarship") else 0,
                "life_at_school_length": len(str(data.get("life_at_school", ""))) if data.get("life_at_school") else 0,
                "infra_and_facilities_length": len(str(data.get("infra_and_facilities", ""))) if data.get("infra_and_facilities") else 0,
                "leader_message_count": len(data.get("leader_messages", [])),
                "event_count": len(data.get("events", [])),
                "news_count": len(data.get("news", []))
            },
            "facility_documentation": {
                "infrastructure_categories": infra_categories,
                "total_features": facility_features
            },
        },
        "fees_analysis": fees_analysis,
        "data_completeness": {
            "basic_info_completion": f"{basic_score:.1f}",
            "academic_info_completion": f"{academic_score:.1f}",
            "contact_info_completion": f"{contact_score:.1f}",
            "fee_completeness_score": fees_analysis.get("fee_completeness_score", 0)
        }
    }
    
    # COLLECT ALL NORMALIZED SCORES FOR CONSISTENCY
    analysis["scores"] = {
        "profile_completeness_score": normalize(profile_completeness_score),
        "data_quality_score": normalize(data_quality_score),
        "content_richness_score": normalize(content_score),
        "visual_content_score": normalize(visual_content_score),
        "contact_accessibility_score": normalize(contact_accessibility_score),
        "academic_information_score": normalize(academic_information_score),
        "infrastructure_score": normalize(infrastructure_score),
        "fee_completeness_score": normalize(analysis["detailed_analysis"].get("data_completeness", {}).get("fee_completeness_score", 0))
    }
    return analysis


def get_profile_scan_delta(slug):
    recent_scans = SchoolProfileScan.objects.filter(slug=slug).order_by("-created_at")[:2]
    if len(recent_scans) < 2:
        return None
    current_score = recent_scans[0].score or 0
    previous_score = recent_scans[1].score or 0
    delta = current_score - previous_score
    percent_change = round((delta / previous_score) * 100, 1) if previous_score else None
    delta_time = recent_scans[0].created_at - recent_scans[1].created_at
    return {
        "current_score": current_score,
        "previous_score": previous_score,
        "delta": delta,
        "percent_change": percent_change,
        "comparison_period": (
            f"{delta_time.total_seconds():.0f} seconds"
            if delta_time.total_seconds() < 60 else
            f"{delta_time.total_seconds() // 60:.0f} minutes"
            if delta_time.total_seconds() < 3600 else
            f"{delta_time.total_seconds() // 3600:.0f} hours"
            if delta_time.total_seconds() < 86400 else
            f"{(recent_scans[0].created_at - recent_scans[1].created_at).days} days"
        )
    }

def smart_field_score(value, weight=1.0, threshold=50):
    if isinstance(value, str):
        return weight if len(value.strip()) >= threshold else 0.5 * weight
    elif isinstance(value, (list, dict)):
        return weight if len(value) else 0
    return 0


def enrich_analysis_with_extras(slug, analysis):
    # Add trend tracking
    trend = get_profile_scan_delta(slug)
    if trend:
        analysis["trend"] = trend

    # Add confidence level
    score = analysis.get("overall_score", 0)
    if score >= 85:
        confidence = "high"
    elif score >= 65:
        confidence = "medium"
    else:
        confidence = "low"
    analysis["confidence_level"] = confidence

    return analysis


def run_complete_school_analysis(slug, data):
    # Step 1: Run the main profile analysis
    base_analysis = analyse_school_profile(data)

    # Step 2: Enrich the analysis with smart add-ons
    enriched_analysis = enrich_analysis_with_extras(slug, base_analysis)

    return enriched_analysis